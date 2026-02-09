import fitz
doc = fitz.open(r"D:\Work\books\Social_prp3_T1_2.pdf")
print(f"Total pages: {len(doc)}")
doc.close()
