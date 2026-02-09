from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

print("Listing first 5 books and their content length:")
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_TITLE, dbms_lob.getlength(BOOK_CONTENT) FROM MY_LIBRARY WHERE ROWNUM <= 5")
for row in cursor.fetchall():
    print(f"Book: {row[0]}, Length: {row[1]}")

print("\nTesting keyword search for 'verb':")
search_query = "%verb%"
cursor.execute("SELECT BOOK_TITLE FROM MY_LIBRARY WHERE LOWER(BOOK_CONTENT) LIKE :1", (search_query,))
results = cursor.fetchall()
print(f"Found {len(results)} books containing 'verb'")
for row in results[:5]:
    print(f"- {row[0]}")

conn.close()
