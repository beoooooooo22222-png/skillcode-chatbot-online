from src.database import Database
import oracledb

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

print("Sequences in DB:")
cursor.execute("SELECT sequence_name FROM all_sequences WHERE sequence_owner = :1", (db.user.upper(),))
for row in cursor.fetchall():
    print(f"- {row[0]}")

conn.close()
