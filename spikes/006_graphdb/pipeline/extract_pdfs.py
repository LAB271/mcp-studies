#!/usr/bin/env python3
"""
Extract text from PDF files in the documents folder
Requires: pip install pdfplumber
"""

import pdfplumber
from pathlib import Path
import sys

def extract_pdf_text(pdf_path, output_path):
    """Extract text from PDF and save to text file."""
    print(f"Extracting text from {pdf_path.name}...")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {i+1} ---\n{page_text}\n\n"
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i+1} pages...")
            
            # Save extracted text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"✓ Extracted {len(pdf.pages)} pages to {output_path.name}")
            print(f"  Size: {len(text) / 1024 / 1024:.2f} MB")
            return True
    
    except Exception as e:
        print(f"✗ Error extracting {pdf_path.name}: {e}")
        return False

def main():
    """Extract all PDFs in documents folder."""
    documents_path = Path(__file__).parent.parent / "graph_data" / "documents"
    
    if not documents_path.exists():
        print(f"Error: {documents_path} does not exist")
        sys.exit(1)
    
    # Find all PDFs
    pdf_files = list(documents_path.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in documents folder")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process\n")
    
    success_count = 0
    for pdf_file in pdf_files:
        output_file = pdf_file.with_suffix('.txt')
        
        # Skip if already extracted
        if output_file.exists():
            print(f"⊘ {output_file.name} already exists, skipping...")
            continue
        
        if extract_pdf_text(pdf_file, output_file):
            success_count += 1
    
    print(f"\n✓ Successfully extracted {success_count}/{len(pdf_files)} PDFs")

if __name__ == "__main__":
    main()
