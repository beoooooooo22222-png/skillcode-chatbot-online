from database import Database
from ocr_utils import OCRProcessor
import oracledb
import logging

logging.basicConfig(level=logging.INFO)
db = Database()
ocr = OCRProcessor()

try:
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Find books with effectively empty content (length 38 is the error message)
    cursor.execute("SELECT BOOK_TITLE, FILE_PATH FROM MY_LIBRARY WHERE dbms_lob.getlength(BOOK_CONTENT) <= 40")
    books = cursor.fetchall()
    print(f"Found {len(books)} books needing repair.")
    
    for title, file_path in books:
        print(f"Repairing: {title}...")
        full_text = ocr.process_pdf(file_path)
        
        if len(full_text) > 40:
            text_var = cursor.var(oracledb.DB_TYPE_CLOB)
            text_var.setvalue(0, full_text)
            cursor.execute("UPDATE MY_LIBRARY SET BOOK_CONTENT = :1 WHERE BOOK_TITLE = :2", (text_var, title))
            conn.commit()
            print(f"  -> ✅ Fixed! New length: {len(full_text)}")
        else:
            print(f"  -> ❌ Still failing: {full_text[:50]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
