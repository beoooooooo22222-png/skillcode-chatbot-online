from src.database import Database
import oracledb

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

print("Checking counts by assistant type:")
cursor.execute("SELECT ASSISTANT_TYPE, count(*) FROM CONVERSATIONS GROUP BY ASSISTANT_TYPE")
for row in cursor.fetchall():
    print(f"Type: {row[0]}, Count: {row[1]}")

print("\nRecent 10 conversations overall:")
cursor.execute("SELECT ID, ASSISTANT_TYPE, USER_MESSAGE FROM CONVERSATIONS ORDER BY CREATED_AT DESC")
for row in cursor.fetchmany(10):
    msg = row[2].read() if hasattr(row[2], 'read') else str(row[2])
    print(f"ID: {row[0]}, Type: {row[1]}, Msg: {msg[:30]}...")

conn.close()
