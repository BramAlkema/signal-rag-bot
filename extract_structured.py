#!/usr/bin/env python3
"""Extract structured content from PDFs preserving TOC, links, tables, and hierarchy"""

import os
import re
from pathlib import Path
import pdfplumber
import fitz  # PyMuPDF

def extract_toc(pdf_path):
    """Extract table of contents using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        doc.close()

        if toc:
            toc_md = "## Table of Contents\n\n"
            for level, title, page in toc:
                indent = "  " * (level - 1)
                toc_md += f"{indent}- [{title}](#) (Page {page})\n"
            return toc_md + "\n"
        return ""
    except Exception as e:
        print(f"  Warning: Could not extract TOC: {e}")
        return ""

def extract_links(pdf_path):
    """Extract all hyperlinks from PDF"""
    links = []
    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            for link in page.get_links():
                if 'uri' in link:
                    links.append({
                        'page': page_num + 1,
                        'url': link['uri']
                    })
        doc.close()
    except Exception as e:
        print(f"  Warning: Could not extract links: {e}")

    return links

def extract_structured_content(pdf_path):
    """Extract content with structure preserved"""
    content = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_content = f"\n\n## Page {page_num + 1}\n\n"

                # Extract text with layout
                text = page.extract_text()
                if text:
                    page_content += text

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table_num, table in enumerate(tables):
                        page_content += f"\n\n### Table {table_num + 1}\n\n"
                        page_content += format_table_as_markdown(table)

                content.append(page_content)

        return "\n".join(content)
    except Exception as e:
        print(f"✗ Failed to extract structured content: {e}")
        return None

def format_table_as_markdown(table):
    """Convert table array to markdown format"""
    if not table or not table[0]:
        return ""

    md = ""
    # Headers
    headers = table[0]
    md += "| " + " | ".join(str(cell or "") for cell in headers) + " |\n"
    md += "|" + "|".join(["---"] * len(headers)) + "|\n"

    # Rows
    for row in table[1:]:
        md += "| " + " | ".join(str(cell or "") for cell in row) + " |\n"

    return md + "\n"

def process_pdf_with_structure(pdf_path, output_dir="intermediate"):
    """Process single PDF preserving all structure"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Processing: {pdf_path.name}")

    # Build structured markdown
    markdown = f"# {pdf_path.stem}\n\n"
    markdown += f"**Source:** {pdf_path.name}\n\n"

    # Extract TOC
    toc = extract_toc(pdf_path)
    if toc:
        markdown += toc

    # Extract main content
    content = extract_structured_content(pdf_path)
    if content:
        markdown += content

    # Extract and append links
    links = extract_links(pdf_path)
    if links:
        markdown += "\n\n## Referenced Links\n\n"
        for link in links:
            markdown += f"- Page {link['page']}: {link['url']}\n"

    # Save
    output_path = Path(output_dir) / f"{pdf_path.stem}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    char_count = len(markdown)
    print(f"  ✓ Saved: {output_path.name} ({char_count:,} chars, ~{char_count//4:,} tokens)")

    return char_count

def process_all_pdfs(input_dir="input/pdfs", output_dir="intermediate"):
    """Process all PDFs with structure preservation"""
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    print(f"Processing {len(pdf_files)} PDFs with structure preservation...\n")

    total_chars = 0
    extracted = 0

    for pdf_path in pdf_files:
        try:
            chars = process_pdf_with_structure(pdf_path, output_dir)
            total_chars += chars
            extracted += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    print(f"\n✓ Successfully extracted {extracted}/{len(pdf_files)} PDFs")
    print(f"  Total content: {total_chars:,} characters (~{total_chars//4:,} estimated tokens)")

if __name__ == "__main__":
    process_all_pdfs()
