
import logging
import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.database_oracle import Database as OracleDB
from src.database import Database as MongoDB
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting migration from Oracle to MongoDB...")
    
    try:
        # Connect to Oracle
        oracle_db = OracleDB()
        logger.info("Connected to Oracle.")
    except Exception as e:
        logger.error(f"Failed to connect to Oracle: {e}")
        return

    try:
        # Connect to Mongo
        mongo_db = MongoDB()
        logger.info("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return

    # 1. Migrate Users
    logger.info("Migrating Users...")
    try:
        conn = oracle_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, EMAIL, PASSWORD_HASH, CREATED_AT FROM USERS")
        
        users_count = 0
        max_id = 0
        
        for row in cursor:
            user_id, email, password_hash, created_at = row
            
            # Upsert into Mongo
            mongo_db.db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "email": email,
                    "password_hash": password_hash,
                    "created_at": created_at or datetime.utcnow()
                }},
                upsert=True
            )
            users_count += 1
            if user_id > max_id:
                max_id = user_id
        
        # Update sequence
        if max_id > 0:
            mongo_db.db.counters.update_one(
                {"_id": "users_seq"},
                {"$set": {"seq": max_id}},
                upsert=True
            )
            
        logger.info(f"Migrated {users_count} users. Updated sequence to {max_id}.")
        
    except Exception as e:
        logger.error(f"Error migrating users: {e}")
    finally:
        if 'conn' in locals(): conn.close()

    # 2. Migrate Library (Books)
    logger.info("Migrating Library (Books)...")
    try:
        conn = oracle_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BOOK_ID, BOOK_TITLE, FILE_PATH, BOOK_CONTENT, CREATED_AT FROM MY_LIBRARY")
        
        books_count = 0
        max_id = 0
        
        for row in cursor:
            book_id, title, file_path, content_clob, created_at = row
            
            # Read CLOB
            content = content_clob.read() if hasattr(content_clob, 'read') else str(content_clob)
            
            mongo_db.db.library.update_one(
                {"id": book_id},
                {"$set": {
                    "book_title": title,
                    "file_path": file_path,
                    "book_content": content,
                    "created_at": created_at or datetime.utcnow()
                }},
                upsert=True
            )
            books_count += 1
            if book_id > max_id:
                max_id = book_id
                
        # Update sequence
        if max_id > 0:
            mongo_db.db.counters.update_one(
                {"_id": "library_seq"},
                {"$set": {"seq": max_id}},
                upsert=True
            )
            
        logger.info(f"Migrated {books_count} books. Updated sequence to {max_id}.")
        
    except Exception as e:
        logger.error(f"Error migrating books: {e}")
    finally:
        if 'conn' in locals(): conn.close()

    # 3. Migrate Conversations
    logger.info("Migrating Conversations...")
    try:
        conn = oracle_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, USER_ID, ASSISTANT_TYPE, USER_MESSAGE, AI_RESPONSE, CREATED_AT FROM CONVERSATIONS")
        
        conv_count = 0
        max_id = 0
        
        for row in cursor:
            conv_id, user_id, asst_type, u_msg_clob, ai_resp_clob, created_at = row
            
            u_msg = u_msg_clob.read() if hasattr(u_msg_clob, 'read') else str(u_msg_clob)
            ai_resp = ai_resp_clob.read() if hasattr(ai_resp_clob, 'read') else str(ai_resp_clob)
            
            mongo_db.db.conversations.update_one(
                {"id": conv_id},
                {"$set": {
                    "user_id": user_id,
                    "assistant_type": asst_type,
                    "user_message": u_msg,
                    "ai_response": ai_resp,
                    "created_at": created_at or datetime.utcnow()
                }},
                upsert=True
            )
            conv_count += 1
            if conv_id > max_id:
                max_id = conv_id
                
        # Update sequence
        if max_id > 0:
            mongo_db.db.counters.update_one(
                {"_id": "conversation_seq"},
                {"$set": {"seq": max_id}},
                upsert=True
            )
            
        logger.info(f"Migrated {conv_count} conversations. Updated sequence to {max_id}.")
        
    except Exception as e:
        logger.error(f"Error migrating conversations: {e}")
    finally:
        if 'conn' in locals(): conn.close()

    logger.info("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
