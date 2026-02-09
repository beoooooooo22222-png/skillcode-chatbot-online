from src.database import Database
import oracledb

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

print("Checking CONVERSATIONS table...")
cursor.execute("SELECT count(*) FROM CONVERSATIONS")
count = cursor.fetchone()[0]
print(f"Total conversations in DB: {count}")

if count > 0:
    cursor.execute("SELECT ID, USER_ID, ASSISTANT_TYPE, CREATED_AT FROM CONVERSATIONS ORDER BY CREATED_AT DESC")
    print("\nRecent 5 conversations:")
    for row in cursor.fetchmany(5):
        print(f"ID: {row[0]}, User: {row[1]}, Type: {row[2]}, Date: {row[3]}")

conn.close()
