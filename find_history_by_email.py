from src.database import Database
import sys

def find_history(email):
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print(f"--- Searching History for Email: {email} ---")
    
    # 1. Find the user ID
    cursor.execute("SELECT ID FROM USERS WHERE LOWER(EMAIL) = LOWER(:1)", (email,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ No user found with email: {email}")
        return
    
    user_id = row[0]
    print(f"User ID: {user_id}")
    
    # 2. Get all conversations
    cursor.execute("""
        SELECT ASSISTANT_TYPE, USER_MESSAGE, AI_RESPONSE, TO_CHAR(CREATED_AT, 'YYYY-MM-DD HH24:MI')
        FROM CONVERSATIONS 
        WHERE USER_ID = :1 
        ORDER BY CREATED_AT DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    if not rows:
        print("Empty history.")
    else:
        print(f"Found {len(rows)} messages:\n")
        for row in rows:
            print(f"[{row[3]}] ({row[0]})")
            msg = row[1].read() if hasattr(row[1], 'read') else str(row[1])
            resp = row[2].read() if hasattr(row[2], 'read') else str(row[2])
            print(f"User: {msg}")
            print(f"AI: {resp[:100]}...")
            print("-" * 50)
            
    conn.close()

if __name__ == "__main__":
    email = input("Enter the email address: ") if len(sys.argv) < 2 else sys.argv[1]
    find_history(email)
