from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_TITLE, dbms_lob.getlength(BOOK_CONTENT) FROM my_library WHERE BOOK_TITLE = 'Arabic_Prep2_SB_T1.pdf'")
row = cursor.fetchone()
if row:
    print(f"Title: {row[0]}, Length: {row[1]}")
cursor.close()
conn.close()
