from database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

try:
    conn = db.get_connection()
    cursor = conn.cursor()
    print("Columns in MY_LIBRARY:")
    cursor.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'MY_LIBRARY'")
    for row in cursor.fetchall():
        print(f"- {row[0]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
