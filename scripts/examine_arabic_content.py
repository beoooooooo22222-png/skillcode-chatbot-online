from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_CONTENT FROM my_library WHERE BOOK_TITLE = 'Arabic_Prep2_SB_T1.pdf'")
row = cursor.fetchone()
if row:
    content = row[0].read()
    print(content[5000:6000]) # Sample from middle
cursor.close()
conn.close()
