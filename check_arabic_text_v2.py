from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

print("Checking snippet of Arabic_prim4_TR2.pdf:")
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_CONTENT FROM MY_LIBRARY WHERE BOOK_TITLE = 'Arabic_prim4_TR2.pdf'")
row = cursor.fetchone()
if row:
    text = row[0].read()
    print(text[:1000])
else:
    print("Book not found!")

conn.close()
