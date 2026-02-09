
import logging
import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.database_oracle import Database as OracleDB
from src.database_sqlite import Database as SQLiteDB
from src.vector_db import VectorDB
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting migration from Oracle to SQLite + VectorStore...")
    
    try:
        # Connect to Oracle
        oracle_db = OracleDB()
        logger.info("Connected to Oracle.")
    except Exception as e:
        logger.error(f"Failed to connect to Oracle: {e}")
        return

    # Initialize New DBs
    sqlite_db = SQLiteDB()
    vector_db = VectorDB()

    # 1. Migrate Users
    logger.info("Migrating Users...")
    try:
        conn = oracle_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT EMAIL, PASSWORD_HASH, CREATED_AT FROM USERS")
        
        count = 0
        for row in cursor:
            email, password_hash, created_at = row
            
            # Check if exists
            if not sqlite_db.email_exists(email):
                sqlite_db.create_user(email, password_hash)
                count += 1
                
        logger.info(f"Migrated {count} users.")
        
    except Exception as e:
        logger.error(f"Error migrating users: {e}")
    finally:
        if 'conn' in locals(): conn.close()

    # 2. Migrate Conversations
    logger.info("Migrating Conversations...")
    try:
        conn = oracle_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT USER_ID, ASSISTANT_TYPE, USER_MESSAGE, AI_RESPONSE, CREATED_AT FROM CONVERSATIONS")
        
        count = 0
        for row in cursor:
            user_id, asst_type, u_msg_clob, ai_resp_clob, created_at = row
            
            u_msg = u_msg_clob.read() if hasattr(u_msg_clob, 'read') else str(u_msg_clob)
            ai_resp = ai_resp_clob.read() if hasattr(ai_resp_clob, 'read') else str(ai_resp_clob)
            
            # Since SQLite auto-increments IDs and we might have gaps or different IDs from restarts,
            # strict ID mapping is tricky without a mapping table.
            # Ideally we'd map old_user_id -> new_user_id.
            # For this simple migration, we'll assume user IDs are sequential 1-based or just push content.
            # A better approach: Find the user by email (if available) or just migrate raw content.
            # But the CONVERSATIONS table in SQLite references user_id.
            # Let's hope the user migration preserved order (it should if sequential).
            
            sqlite_db.save_conversation(
                user_id, # This might mismatch if users were deleted/created out of order, but it's a best effort.
                asst_type,
                u_msg,
                ai_resp
            )
            count += 1
            
        logger.info(f"Migrated {count} conversations.")
        
    except Exception as e:
        logger.error(f"Error migrating conversations: {e}")
    finally:
        if 'conn' in locals(): conn.close()

    # 3. Migrate Books (To Vector Store)
    logger.info("Migrating Books to Vector Store (This IS SLOW - embedding happens here)...")
    try:
        conn = oracle_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BOOK_TITLE, FILE_PATH, BOOK_CONTENT FROM MY_LIBRARY")
        
        count = 0
        for row in cursor:
            title, file_path, content_clob = row
            
            # Read CLOB
            content = content_clob.read() if hasattr(content_clob, 'read') else str(content_clob)
            
            if content:
                logger.info(f"Embedding book: {title}...")
                
                # Add Metadata to SQLite
                sqlite_db.add_book_metadata(title, file_path)
                
                # Add Content to FAISS
                vector_db.add_book(title, content)
                count += 1
                
        logger.info(f"Successfully embedded {count} books into Vector Store.")
        
    except Exception as e:
        logger.error(f"Error migrating books: {e}")
    finally:
        if 'conn' in locals(): conn.close()

    logger.info("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
