from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()

# Check a few different books
books_to_check = ["Arabic_Prep2_SB_T1.pdf", "Math_AR_Prp2_Tr1.pdf", "English_Prim1_Tr2.pdf"]

for title in books_to_check:
    cursor.execute("SELECT BOOK_CONTENT FROM MY_LIBRARY WHERE BOOK_TITLE = :1", (title,))
    row = cursor.fetchone()
    if row:
        content = row[0].read()
        print(f"\n--- Content Sample for {title} ---")
        print(content[2000:4000]) # Get a middle slice
    else:
        print(f"\n--- {title} not found ---")

cursor.close()
conn.close()
