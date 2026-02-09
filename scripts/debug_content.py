from database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

try:
    conn = db.get_connection()
    cursor = conn.cursor()
    title = "English_Prim1_Tr2.pdf"
    print(f"Checking content for: {title}")
    cursor.execute("SELECT dbms_lob.getlength(BOOK_CONTENT), BOOK_CONTENT FROM MY_LIBRARY WHERE BOOK_TITLE = :1", (title,))
    row = cursor.fetchone()
    if row:
        length = row[0]
        content = row[1].read() if row[1] else ""
        print(f"Content Length: {length} characters")
        print("First 500 characters of content:")
        print("-" * 50)
        print(content[:1000])
        print("-" * 50)
    else:
        print("Book not found in database.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
