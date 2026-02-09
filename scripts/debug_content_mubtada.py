from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT BOOK_CONTENT FROM my_library WHERE BOOK_TITLE = 'Arabic_Prep2_SB_T1.pdf'")
row = cursor.fetchone()
if row:
    content = row[0].read()
    print("Content Length:", len(content))
    # Search for anything Greek/Arabic
    import re
    words = re.findall(r'[\u0600-\u06FF]+', content)
    print("Sample words:", words[:50])
    
    # Check for 'مبتد'
    match = re.search(r'مبتدا?', content)
    if match:
        print("MATCH FOUND at:", match.start())
        print("Context:", content[match.start()-50:match.start()+50])
    else:
        print("NO MATCH for 'مبتدا'")
cursor.close()
conn.close()
