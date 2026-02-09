from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_CONTENT FROM my_library WHERE BOOK_TITLE = 'Social_prp3_T1_2.pdf'")
row = cursor.fetchone()
if row:
    content = row[0].read()
    print(content[:1000])
cursor.close()
conn.close()
