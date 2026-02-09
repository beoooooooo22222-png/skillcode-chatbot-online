from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

search_term = "كان"
print(f"Searching for '{search_term}'...")
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_TITLE, dbms_lob.getlength(BOOK_CONTENT) FROM MY_LIBRARY WHERE LOWER(BOOK_CONTENT) LIKE :1", (f"%{search_term}%",))
rows = cursor.fetchall()
print(f"Found {len(rows)} books.")
for row in rows:
    print(f"- {row[0]} (Length: {row[1]})")

search_term2 = "اخواتها"
print(f"\nSearching for '{search_term2}'...")
cursor.execute("SELECT BOOK_TITLE FROM MY_LIBRARY WHERE LOWER(BOOK_CONTENT) LIKE :1", (f"%{search_term2}%",))
rows2 = cursor.fetchall()
print(f"Found {len(rows2)} books.")
for row in rows2:
    print(f"- {row[0]}")

conn.close()
