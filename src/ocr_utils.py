import logging
logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    from rapidocr_onnxruntime import RapidOCR
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logger.warning("OCR libraries (pymupdf, rapidocr-onnxruntime) not installed. Fallback to basic extraction.")

def normalize_arabic(text):
    """Standardize Arabic characters and remove diacritics for easier searching"""
    if not text: return ""
    import re
    # Remove Arabic diacritics (Tashkeel)
    tashkeel_marks = re.compile(r'[\u064B-\u0652]')
    text = tashkeel_marks.sub('', text)
    # Standardize Alef
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    # Standardize Teh Marbuta
    text = text.replace('ة', 'ه')
    # Standardize Yaa
    text = text.replace('ى', 'ي')
    return text

class OCRProcessor:
    def __init__(self):
        self.engine = None
        if HAS_OCR:
            try:
                self.engine = RapidOCR()
                logger.info("RapidOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize RapidOCR: {e}")
                self.engine = None

    def process_pdf(self, file_path):
        """Process PDF and return text with page markers, using OCR where needed."""
        if not HAS_OCR:
            # Fallback to PyPDF2 if OCR libs not missing
            from PyPDF2 import PdfReader
            try:
                reader = PdfReader(file_path)
                full_text = ""
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        full_text += f"\n--- Page {i+1} ---\n{text}\n"
                    else:
                        full_text += f"\n--- Page {i+1} [IMAGE/OCR NEEDED] ---\n"
                return full_text
            except Exception as e:
                return f"Error with basic extraction: {e}"

        if not self.engine:
            return "OCR Engine missing but libs installed."

        full_text = ""
        import re
        try:
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                # Try standard text extraction first
                text = page.get_text().strip()
                
                # Check if text is "junk" (too many l, i, |, /, etc. and no Arabic/English words)
                is_junk = False
                if text:
                    # If it has some text, check if it's rubbish
                    # Egyptian books should have Arabic or English words
                    has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
                    has_english = bool(re.search(r'[a-zA-Z]{3,}', text))
                    
                    if not has_arabic and not has_english:
                        is_junk = True
                    elif len(text) > 100:
                        # High density of symbols/single chars often means bad encoding
                        weird_chars = len(re.findall(r'[|/\\_l1iI]', text))
                        if weird_chars / len(text) > 0.4:
                            is_junk = True
                
                if text and not is_junk:
                    full_text += f"\n--- Page {i+1} ---\n{normalize_arabic(text)}\n"
                else:
                    # If no text or junk text, perform OCR
                    logger.info(f"Page {i+1} {'is empty' if not text else 'looks like junk'}. Performing OCR...")
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Better resolution
                    img_data = pix.tobytes("png")
                    
                    # Run OCR
                    result, _ = self.engine(img_data)
                    
                    if result:
                        ocr_text = "\n".join([line[1] for line in result])
                        full_text += f"\n--- Page {i+1} [OCR] ---\n{normalize_arabic(ocr_text)}\n"
                    else:
                        full_text += f"\n--- Page {i+1} [EMPTY] ---\n"
            
            doc.close()
            
            # Final check - if literally zero text, try PyPDF2
            if not full_text.strip():
                 from PyPDF2 import PdfReader
                 reader = PdfReader(file_path)
                 for i, page in enumerate(reader.pages):
                     p_text = page.extract_text() or ""
                     if p_text.strip():
                         full_text += f"\n--- Page {i+1} ---\n{normalize_arabic(p_text)}\n"

            return full_text
        except Exception as e:
            logger.error(f"Error in process_pdf: {e}")
            return f"Error processing file with OCR: {e}"

if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    import sys
    if len(sys.argv) > 1:
        processor = OCRProcessor()
        print(processor.process_pdf(sys.argv[1]))
