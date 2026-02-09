
import os
import sys
import logging
from src.database import Database
from src.ocr_utils import OCRProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForceIndex")

BOOKS_DIR = r"D:\Work\books"

def force_index_english():
    db = Database()
    ocr = OCRProcessor()
    
    logger.info("Starting force indexing of English books...")
    
    indexed_count = 0
    
    # We'll search for English specifically
    for root, dirs, files in os.walk(BOOKS_DIR):
        for f in files:
            if f.endswith('.pdf') and 'english' in f.lower():
                file_path = os.path.join(root, f)
                logger.info(f"Indexing English book: {f}")
                
                try:
                    text = ocr.process_pdf(file_path)
                    if text and text.strip():
                        db.add_book(f, file_path, text)
                        indexed_count += 1
                        logger.info(f"✅ Indexed: {f}")
                    else:
                        logger.warning(f"No text extracted from {f}")
                except Exception as e:
                    logger.error(f"Error indexing {f}: {e}")
    
    logger.info(f"Completed! Indexed {indexed_count} English books.")

if __name__ == "__main__":
    force_index_english()
