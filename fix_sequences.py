
from src.database import Database
import oracledb

def fix_sequences():
    try:
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        sequences = [
            "library_seq",
            "users_seq",
            "CONVERSATION_SEQ"
        ]
        
        for seq in sequences:
            try:
                cursor.execute(f"SELECT {seq}.NEXTVAL FROM dual")
                print(f"✅ Sequence {seq} already exists")
            except oracledb.DatabaseError as e:
                error_obj, = e.args
                if error_obj.code == 2289: # ORA-02289: sequence does not exist
                    print(f"🔧 Creating sequence {seq}...")
                    cursor.execute(f"CREATE SEQUENCE {seq} START WITH 1 INCREMENT BY 1")
                    print(f"✅ Sequence {seq} created")
                else:
                    print(f"❌ Error checking sequence {seq}: {e}")
        
        conn.commit()
        conn.close()
        print("\nAll sequences verified!")
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    fix_sequences()
