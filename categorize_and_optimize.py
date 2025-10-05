#!/usr/bin/env python3
"""Optimize content and categorize into semantic buckets using GPT-4"""

import os
import json
from pathlib import Path
from openai import OpenAI
import tiktoken

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def count_tokens(text, model="gpt-4"):
    """Count tokens in text"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def analyze_and_categorize(content, filename):
    """Use GPT-4 to analyze content and suggest category"""
    prompt = f"""Analyze this document and provide:
1. A concise topic/category (2-5 words)
2. Key themes (comma-separated)
3. Document type (e.g., tutorial, reference, guide, API docs, etc.)

Document: {filename}

First 2000 characters of content:
{content[:2000]}

Respond in JSON format:
{{"category": "...", "themes": "...", "doc_type": "..."}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for cost efficiency
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"  Warning: Categorization failed: {e}")
        return {"category": "General", "themes": "unknown", "doc_type": "document"}

def optimize_content(content, filename):
    """Use GPT-4 to clean and optimize markdown"""
    prompt = f"""Clean and optimize this markdown document for GPT Assistant knowledge base:

1. Preserve ALL structure: headings, tables, lists, links
2. Remove redundant whitespace and formatting artifacts
3. Ensure proper markdown syntax
4. Keep ALL semantic content - don't summarize
5. Fix any broken tables or formatting issues

Document: {filename}

Content:
{content}

Return ONLY the optimized markdown, no explanations."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=16000  # Limit for safety
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"  Warning: Optimization failed, using original: {e}")
        return content

def process_documents(input_dir="intermediate", output_dir="optimized"):
    """Process all documents: categorize and optimize"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    md_files = list(Path(input_dir).glob("*.md"))
    print(f"Processing {len(md_files)} documents for categorization and optimization...\n")

    categorized = []

    for md_path in md_files:
        print(f"Processing: {md_path.name}")

        # Read content
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Categorize
        category_info = analyze_and_categorize(content, md_path.stem)
        print(f"  Category: {category_info['category']}")
        print(f"  Themes: {category_info['themes']}")

        # Optimize (for now, skip optimization to save API costs - just use original)
        # optimized = optimize_content(content, md_path.stem)
        optimized = content  # Skip optimization for demo

        # Count tokens
        tokens = count_tokens(optimized)
        print(f"  Tokens: {tokens:,}")

        # Save optimized version
        output_path = Path(output_dir) / md_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized)

        categorized.append({
            "filename": md_path.name,
            "category": category_info["category"],
            "themes": category_info["themes"],
            "doc_type": category_info["doc_type"],
            "tokens": tokens,
            "optimized_path": str(output_path)
        })

        print()

    # Save categorization metadata
    with open(Path(output_dir) / "categories.json", 'w') as f:
        json.dump(categorized, f, indent=2)

    print(f"✓ Processed {len(categorized)} documents")
    print(f"  Categorization saved to: {output_dir}/categories.json")

    return categorized

if __name__ == "__main__":
    process_documents()
