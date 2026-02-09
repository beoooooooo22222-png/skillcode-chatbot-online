
import os
import sys
import logging
from src.database import Database
from src.OCRProcessor import OCRProcessor # Wait, it's OCRProcessor in src.ocr_utils
from src.ocr_utils import OCRProcessor as ActualOCRProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FullSync")

BOOKS_DIR = r"D:\Work\books"

def full_sync():
    db = Database()
    ocr = ActualOCRProcessor()
    
    logger.info(f"Starting FULL SYNC from {BOOKS_DIR}...")
    
    indexed_count = 0
    skipped_count = 0
    
    for root, dirs, files in os.walk(BOOKS_DIR):
        for f in files:
            if f.endswith('.pdf'):
                file_path = os.path.join(root, f)
                
                # Check if already in SQLite library
                # (Assuming we want to skip if title exists in SQLite)
                # But here we want to make sure it's in Vector Store too.
                # A better way is to check the Vector Store specifically, 
                # but adding to FAISS is idempotent-ish if we don't mind duplicates 
                # or we check metadata.
                
                logger.info(f"Processing: {f}")
                
                try:
                    text = ocr.process_pdf(file_path)
                    if text and text.strip():
                        # add_book in database.py handles both SQLite and Vector
                        # It uses "INSERT OR IGNORE" in SQLite
                        success = db.add_book(f, file_path, text)
                        if success:
                            indexed_count += 1
                            logger.info(f"✅ Indexed: {f}")
                        else:
                            skipped_count += 1
                            logger.info(f"⏭️ Skipped (Already indexed?): {f}")
                    else:
                        logger.warning(f"No text extracted from {f}")
                except Exception as e:
                    logger.error(f"Error indexing {f}: {e}")
    
    logger.info(f"Full Sync Completed! Indexed {indexed_count}, Skipped {skipped_count}.")

if __name__ == "__main__":
    full_sync()
