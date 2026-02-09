from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

print("Checking snippet of Arabic_prim4_TR2.pdf:")
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT dbms_lob.substr(BOOK_CONTENT, 4000, 1) FROM MY_LIBRARY WHERE BOOK_TITLE = 'Arabic_prim4_TR2.pdf'")
row = cursor.fetchone()
if row:
    print(row[0])
else:
    print("Book not found!")

conn.close()
