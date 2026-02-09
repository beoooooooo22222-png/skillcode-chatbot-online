from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
title = "English_Prim1_Tr2.pdf"
cursor.execute("SELECT BOOK_CONTENT FROM MY_LIBRARY WHERE BOOK_TITLE = :1", (title,))
row = cursor.fetchone()
if row:
    content = row[0].read()
    print(f"Content Sample for {title}:")
    print(content[:2000])
cursor.close()
conn.close()
