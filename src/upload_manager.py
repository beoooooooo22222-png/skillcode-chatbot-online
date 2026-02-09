import os
import oracledb
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
BOOKS_DIR = r"D:\Work\books"
DB_USER = "help_me"
DB_PASS = "password"
DB_DSN  = "localhost:1521/xe"

# *** YOUR SPECIFIC PATH ***
CLIENT_DIR = r"C:\oraclexe\app\oracle\instantclient_23_0"

try:
    oracledb.init_oracle_client(lib_dir=CLIENT_DIR)
except Exception as e:
    print(f"⚠️ Driver Init Error: {e}")
# **************************
from src.ocr_utils import OCRProcessor

# Initialize OCR Processor
ocr = OCRProcessor()

print("--- STARTING BOOK UPLOAD ---")

# 1. Connect to Oracle
try:
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cursor = conn.cursor()
    print("✅ Connected to Oracle Database.")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit()

# 2. Process Files
if os.path.exists(BOOKS_DIR):
    files = [f for f in os.listdir(BOOKS_DIR) if f.endswith('.pdf')]
    print(f"📂 Found {len(files)} PDFs in {BOOKS_DIR}")

    for filename in files:
        file_path = os.path.join(BOOKS_DIR, filename)
        print(f"   Processing: {filename}...")

        try:
            # Use OCR Processor (handles text and images)
            full_text = ocr.process_pdf(file_path)
            
            if not full_text.strip() or "[EMPTY]" in full_text:
                print(f"     -> ⚠️ Warning: Little to no text was extracted from {filename}.")

            # Prepare CLOB
            text_var = cursor.var(oracledb.DB_TYPE_CLOB)
            text_var.setvalue(0, full_text)

            # Check for duplicates using correct column name
            cursor.execute("SELECT count(*) FROM MY_LIBRARY WHERE BOOK_TITLE = :1", (filename,))
            if cursor.fetchone()[0] == 0:
                # Insert using correct column names and sequence
                sql = "INSERT INTO MY_LIBRARY (BOOK_ID, BOOK_TITLE, FILE_PATH, BOOK_CONTENT) VALUES (library_seq.NEXTVAL, :1, :2, :3)"
                cursor.execute(sql, (filename, file_path, text_var))
                conn.commit()
                print(f"     -> ✅ Saved with OCR support!")
            else:
                # Option: Update existing content if it was empty before
                print(f"     -> ⚠️ Already exists. Updating content...")
                sql = "UPDATE MY_LIBRARY SET BOOK_CONTENT = :1 WHERE BOOK_TITLE = :2"
                cursor.execute(sql, (text_var, filename))
                conn.commit()
                print(f"     -> ✅ Updated!")
        except Exception as e:
            print(f"     -> ❌ Error: {e}")
else:
    print(f"❌ Error: Folder {BOOKS_DIR} not found.")

cursor.close()
conn.close()
print("--- DONE ---")