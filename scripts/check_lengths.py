from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_TITLE, dbms_lob.getlength(BOOK_CONTENT) FROM MY_LIBRARY ORDER BY UPLOAD_DATE DESC")
for row in cursor.fetchall():
    print(f"Book: {row[0]}, Length: {row[1]}")
cursor.close()
conn.close()
