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
    
    # Target all Arabic-content books
    cursor.execute("""
        SELECT BOOK_TITLE, FILE_PATH 
        FROM MY_LIBRARY 
        WHERE BOOK_TITLE LIKE 'Arabic%' 
           OR BOOK_TITLE LIKE 'Islamic%' 
           OR BOOK_TITLE LIKE '%_AR_%'
    """)
    books = cursor.fetchall()
    
    for title, file_path in books:
        print(f"Repairing Arabic book: {title}...")
        # Force re-process to get normalized (no diacritics) and OCR'd content
        full_text = ocr.process_pdf(file_path)
        
        if len(full_text) > 100:
            text_var = cursor.var(oracledb.DB_TYPE_CLOB)
            text_var.setvalue(0, full_text)
            cursor.execute("UPDATE MY_LIBRARY SET BOOK_CONTENT = :1 WHERE BOOK_TITLE = :2", (text_var, title))
            conn.commit()
            print(f"  -> ✅ Repaired! New length: {len(full_text)}")
        else:
            print(f"  -> ❌ Failed to extract content for {title}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
