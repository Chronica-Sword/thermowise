import fitz  # PyMuPDF
import sys

pdf_path = r"d:\J.M. Smith, Hendrick Van Ness, Michael Abbott, Mark Swihart - Introduction to Chemical Engineering Thermodynamics-McGraw-Hill Education (2018).pdf"

try:
    doc = fitz.open(pdf_path)
    print(f"Total Pages: {doc.page_count}")
    
    # Extract Table of Contents
    toc = doc.get_toc()
    print("Table of Contents (First 20 items):")
    for item in toc[:20]:
        print(item)
        
    # Check for specific appendix (Steam Tables usually in Appendix E/F)
    print("\nSearching for Property Tables in TOC...")
    for item in toc:
        if "Table" in item[1] or "Steam" in item[1] or "Appendix" in item[1]:
            print(item)

    doc.close()
except Exception as e:
    print(f"Error: {e}")
