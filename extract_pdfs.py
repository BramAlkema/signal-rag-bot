#!/usr/bin/env python3
"""Extract text from PDFs"""

import os
from pathlib import Path
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n\n--- Page {page_num + 1} ---\n\n"
                text += page_text

        return text.strip()
    except Exception as e:
        print(f"✗ Failed to extract {pdf_path}: {e}")
        return None

def process_all_pdfs(input_dir="input/pdfs", output_dir="intermediate"):
    """Process all PDFs and save as individual markdown files"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    pdf_files = list(Path(input_dir).glob("*.pdf"))
    print(f"Processing {len(pdf_files)} PDFs...\n")

    extracted = 0
    total_chars = 0

    for pdf_path in pdf_files:
        text = extract_text_from_pdf(pdf_path)
        if text:
            # Save as markdown
            output_path = Path(output_dir) / f"{pdf_path.stem}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {pdf_path.stem}\n\n")
                f.write(f"Source: {pdf_path.name}\n\n")
                f.write(text)

            char_count = len(text)
            total_chars += char_count
            print(f"✓ Extracted: {pdf_path.name} → {output_path.name} ({char_count:,} chars)")
            extracted += 1
        else:
            print(f"✗ Skipped: {pdf_path.name}")

    print(f"\n✓ Successfully extracted {extracted}/{len(pdf_files)} PDFs")
    print(f"  Total content: {total_chars:,} characters (~{total_chars//4:,} estimated tokens)")

if __name__ == "__main__":
    process_all_pdfs()
