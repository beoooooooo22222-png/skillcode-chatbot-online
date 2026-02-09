
import sys
import os
sys.path.append(os.getcwd())

from src.database_oracle import Database as OracleDB
from src.database_sqlite import Database as SQLiteDB
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def verify():
    print("\n" + "="*50)
    print("      DATA SYNC VERIFICATION: ORACLE <-> VECTOR")
    print("="*50)
    
    # 1. Check Local (SQLite/Vector)
    try:
        sqlite_db = SQLiteDB()
        local_books = sqlite_db.get_all_books()
        local_titles = {b['title'] for b in local_books}
        print(f"✅ Local Books (SQLite/Vector): {len(local_titles)}")
        if len(local_titles) > 0:
            print(f"   First 3 local books: {', '.join(sorted(list(local_titles))[:3])}...")
    except Exception as e:
        print(f"❌ Error reading local SQLite: {e}")
        return

    # 2. Check Oracle
    try:
        oracle_db = OracleDB()
        oracle_books = oracle_db.get_all_books()
        oracle_titles = {b['title'] for b in oracle_books}
        print(f"✅ Oracle Database Books:      {len(oracle_titles)}")
        
        # 3. Compare
        missing = oracle_titles - local_titles
        extra = local_titles - oracle_titles
        
        if not missing and not extra:
            print("\n✨ STATUS: PERFECTLY SYNCED!")
        else:
            if missing:
                print(f"\n❌ MISSING IN VECTOR DB ({len(missing)} books):")
                for t in sorted(missing):
                    print(f"  - {t}")
                print("\n👉 ACTION: Run 'python migrate_oracle_to_vector.py' to sync missing books.")
            
            if extra:
                print(f"\nℹ️  ONLY IN VECTOR DB ({len(extra)} books):")
                for t in sorted(extra):
                    print(f"  - {t}")
                print("   (These are books migrated previously or added manually to Vector DB)")

    except Exception as e:
        print(f"\n❌ Could not connect to Oracle: {e}")
        print("   Checking if you have Oracle Client/Environment variables set up...")

if __name__ == "__main__":
    verify()
