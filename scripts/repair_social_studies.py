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
    
    # Targeting the Social Studies book specifically
    title = 'Social_prp3_T1_2.pdf'
    cursor.execute("SELECT FILE_PATH FROM MY_LIBRARY WHERE BOOK_TITLE = :1", (title,))
    row = cursor.fetchone()
    
    if row:
        file_path = row[0]
        print(f"Force re-processing: {title} from {file_path}...")
        full_text = ocr.process_pdf(file_path)
        
        if len(full_text) > 1000: # Ensure we got significant content
            text_var = cursor.var(oracledb.DB_TYPE_CLOB)
            text_var.setvalue(0, full_text)
            cursor.execute("UPDATE MY_LIBRARY SET BOOK_CONTENT = :1 WHERE BOOK_TITLE = :2", (text_var, title))
            conn.commit()
            print(f"  -> ✅ Fixed! New length: {len(full_text)}")
        else:
            print(f"  -> ❌ Extraction too short: {len(full_text)} chars.")
    else:
        print(f"  -> ❌ Book not found in library.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
