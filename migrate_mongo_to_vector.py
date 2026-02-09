
import logging
import sys
import os

from src.database_mongo import Database as MongoDB
from src.database_sqlite import Database as SQLiteDB
from src.vector_db import VectorDB
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting migration from MongoDB to SQLite + VectorStore...")
    
    try:
        mongo_db = MongoDB()
        logger.info("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return

    sqlite_db = SQLiteDB()
    vector_db = VectorDB()

    # 1. Migrate Users
    logger.info("Migrating Users...")
    try:
        users = mongo_db.db.users.find({})
        count = 0
        for user in users:
            # Check if exists
            if not sqlite_db.email_exists(user['email']):
                sqlite_db.create_user(user['email'], user.get('password_hash'))
                count += 1
        logger.info(f"Migrated {count} users.")
    except Exception as e:
        logger.error(f"Error migrating users: {e}")

    # 2. Migrate Conversations
    logger.info("Migrating Conversations...")
    try:
        convs = mongo_db.db.conversations.find({})
        count = 0
        for c in convs:
            # We use email logic ideally, but IDs are integers in both
            # If we just copy raw data, we assume IDs align.
            # SQLite auto-increments.
            # For simplicity, we just insert.
            sqlite_db.save_conversation(
                c['user_id'],
                c.get('assistant_type', 'general'),
                c['user_message'],
                c['ai_response']
            )
            count += 1
        logger.info(f"Migrated {count} conversations.")
    except Exception as e:
        logger.error(f"Error migrating conversations: {e}")

    # 3. Migrate Books (To Vector Store)
    logger.info("Migrating Books to Vector Store (This may take time)...")
    try:
        books = mongo_db.db.library.find({})
        count = 0
        for b in books:
            title = b['book_title']
            content = b.get('book_content', '')
            file_path = b.get('file_path', '')
            
            if content:
                logger.info(f"Embedding book: {title}...")
                
                # Add Metadata to SQLite
                sqlite_db.add_book_metadata(title, file_path)
                
                # Add Content to FAISS
                vector_db.add_book(title, content)
                count += 1
        logger.info(f"Migrated {count} books to vector store.")
    except Exception as e:
        logger.error(f"Error migrating books: {e}")

    logger.info("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
