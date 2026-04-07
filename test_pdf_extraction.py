import pdfplumber
import os

pdf_path = "app/data/temp_SNA-Case_Study-1134.pdf"
absolute_path = os.path.abspath(pdf_path)

print(f"Testing extraction for: {absolute_path}")

try:
    with pdfplumber.open(absolute_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                print(f"--- Page {i+1} ---")
                print(text[:200] + "...") # Print first 200 chars
            else:
                print(f"--- Page {i+1} ---")
                print("[NO TEXT EXTRACTED]")
except Exception as e:
    print(f"Error: {e}")
