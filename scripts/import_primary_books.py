import os
import logging
from database import Database
from ocr_utils import OCRProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_primary_books():
    db = Database()
    ocr = OCRProcessor()
    base_path = r"D:\Work\books"
    
    # We look for folders Primary1, Primary2...
    for i in range(1, 7):
        folder_name = f"Primary{i}"
        folder_path = os.path.join(base_path, folder_name)
        
        if not os.path.exists(folder_path):
            logger.warning(f"Folder {folder_path} not found. Skipping.")
            continue
            
        logger.info(f"Processing folder: {folder_name}...")
        
        for file in os.listdir(folder_path):
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(folder_path, file)
                logger.info(f"  Reading: {file}...")
                
                # Use our high-quality OCR pipeline
                content = ocr.process_pdf(file_path)
                
                if len(content.strip()) > 100:
                    # Level is "Primary 1", "Primary 2", etc.
                    level = f"Primary {i}"
                    success = db.add_book(file, file_path, content, level)
                    if success:
                        logger.info(f"    ✅ Uploaded to {level}")
                    else:
                        logger.info(f"    ℹ️ Already exists in database.")
                else:
                    logger.error(f"    ❌ Failed to extract content for {file}")

if __name__ == "__main__":
    upload_primary_books()
