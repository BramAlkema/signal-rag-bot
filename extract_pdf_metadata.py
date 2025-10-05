#!/usr/bin/env python3
"""Extract metadata and first page text from PDFs to identify them"""
import os
import json
from pathlib import Path
import PyPDF2

def extract_metadata(pdf_path):
    """Extract metadata and first lines from PDF"""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Get metadata
            metadata = reader.metadata or {}
            
            # Get first page text (first 500 chars)
            first_page = ""
            if len(reader.pages) > 0:
                first_page = reader.pages[0].extract_text()[:500]
            
            return {
                'file': os.path.basename(pdf_path),
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'pages': len(reader.pages),
                'first_text': first_page.strip()
            }
    except Exception as e:
        return {
            'file': os.path.basename(pdf_path),
            'error': str(e)
        }

if __name__ == "__main__":
    pdf_dir = Path("input/pdfs")
    pdfs = list(pdf_dir.glob("*.pdf"))
    
    results = []
    for pdf in sorted(pdfs):
        print(f"Extracting: {pdf.name}")
        meta = extract_metadata(pdf)
        results.append(meta)
    
    # Save to JSON
    with open("pdf_metadata.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExtracted metadata from {len(results)} PDFs")
    print("Saved to: pdf_metadata.json")
