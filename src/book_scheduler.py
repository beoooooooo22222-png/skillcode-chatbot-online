"""
Daily Book Upload Scheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
import os
from PyPDF2 import PdfReader
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BOOKS_DIR = "books"

def upload_books(db):
    """Upload books from folder to database"""
    # Ensure books directory exists
    if not os.path.exists(BOOKS_DIR):
        try:
            os.makedirs(BOOKS_DIR)
            logger.info(f"Created books directory: {BOOKS_DIR}")
        except OSError:
            logger.warning(f"Could not create books directory: {BOOKS_DIR}")
            return
    
    try:
        pdf_files = []
        for root, dirs, files in os.walk(BOOKS_DIR):
            for f in files:
                if f.endswith('.pdf'):
                    # Store relative path or just filename based on how you want to track it
                    # The current logic uses filename as title
                    pdf_files.append(os.path.join(root, f))
        
        if not pdf_files:
            logger.info("No PDF files found to upload")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process (recursive)")
        
        from src.ocr_utils import OCRProcessor
        ocr = OCRProcessor()
        
        for file_path in pdf_files:
            filename = os.path.basename(file_path)
            logger.info(f"Processing: {filename}...")
            
            try:
                # Use OCR Processor (handles text and images)
                full_text = ocr.process_pdf(file_path)
                
                if not full_text.strip():
                    logger.warning(f"No text extracted from {filename}")
                    continue
                
                # Add to database
                success = db.add_book(filename, file_path, full_text)
                
                if success:
                    logger.info(f"✅ Successfully uploaded: {filename}")
                else:
                    logger.info(f"⚠️ Book already exists: {filename}")
            
            except Exception as e:
                logger.error(f"❌ Error processing {filename}: {e}")
        
        logger.info("Book upload completed")
    
    except Exception as e:
        logger.error(f"Book upload scheduler error: {e}")

def start_book_scheduler(db):
    """Start the background scheduler for daily book uploads"""
    try:
        scheduler = BackgroundScheduler()
        
        # Schedule daily at 2:00 AM
        scheduler.add_job(
            func=upload_books,
            args=(db,),
            trigger="cron",
            hour=2,
            minute=0,
            id='book_upload_job',
            name='Daily Book Upload',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("✅ Book upload scheduler started (runs daily at 2:00 AM)")
    
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
