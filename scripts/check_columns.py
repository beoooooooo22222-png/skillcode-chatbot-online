from database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
# Note: Oracle stores table names in UPPER CASE by default
cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'MY_LIBRARY'")
for row in cursor.fetchall():
    print(row[0])
cursor.close()
conn.close()
