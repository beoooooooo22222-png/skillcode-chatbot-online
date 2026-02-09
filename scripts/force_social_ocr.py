from ocr_utils import OCRProcessor
import logging

logging.basicConfig(level=logging.INFO)
ocr = OCRProcessor()
file_path = r"D:\Work\books\Social_prp3_T1_2.pdf"

print("Processing Social Studies book...")
# Only process first 20 pages for testing
import fitz
doc = fitz.open(file_path)
full_text = ""
for i in range(min(20, len(doc))):
    page = doc[i]
    text = page.get_text().strip()
    if not text or len(text) < 50: # Force OCR if text is suspicious
        print(f"Page {i+1}: Weak/No text. Forcing OCR...")
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        result, _ = ocr.engine(img_data)
        if result:
            ocr_text = "\n".join([line[1] for line in result])
            print(f"  OCR Text Sample: {ocr_text[:100]}")
            full_text += f"\n--- Page {i+1} [OCR] ---\n{ocr_text}\n"
    else:
        print(f"  Standard Text Sample: {text[:100]}")
        full_text += f"\n--- Page {i+1} ---\n{text}\n"
doc.close()

with open("social_debug_output.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
print("Done. Saved to social_debug_output.txt")
