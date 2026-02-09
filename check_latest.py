from src.database import Database
import oracledb

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("SELECT ID, USER_ID, ASSISTANT_TYPE, CREATED_AT FROM CONVERSATIONS ORDER BY CREATED_AT DESC")
row = cursor.fetchone()
if row:
    print(f"LATEST MESSAGE - ID: {row[0]}, User ID: {row[1]}, Type: {row[2]}, Date: {row[3]}")

conn.close()
