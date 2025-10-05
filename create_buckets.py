#!/usr/bin/env python3
"""Create semantic buckets from optimized documents with token counting"""

import json
from pathlib import Path
from collections import defaultdict
import tiktoken

def count_tokens(text, model="gpt-4"):
    """Count tokens accurately"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def simple_categorize(filename, content):
    """Simple keyword-based categorization"""
    content_lower = content.lower()

    # Simple categorization based on keywords
    categories = {
        "API & Integration": ["api", "endpoint", "request", "response", "authentication", "webhook"],
        "Database & Data": ["database", "sql", "query", "schema", "migration", "model"],
        "Frontend & UI": ["react", "component", "ui", "interface", "frontend", "css", "html"],
        "Backend & Server": ["server", "backend", "route", "middleware", "controller"],
        "Security & Auth": ["security", "authentication", "authorization", "permission", "token", "oauth"],
        "DevOps & Deploy": ["deploy", "docker", "kubernetes", "ci/cd", "pipeline", "infrastructure"],
        "Testing": ["test", "testing", "unit test", "integration", "qa"],
        "Documentation": ["guide", "tutorial", "documentation", "readme", "overview"],
    }

    scores = {}
    for category, keywords in categories.items():
        score = sum(content_lower.count(keyword) for keyword in keywords)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)
    return "General Documentation"

def create_semantic_buckets(input_dir="optimized", output_dir="output", max_tokens=2000000):
    """Create semantic buckets with token-aware packing"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load all documents
    md_files = list(Path(input_dir).glob("*.md"))
    print(f"Creating semantic buckets from {len(md_files)} documents...")
    print(f"Target: Max {max_tokens:,} tokens per bucket\n")

    # Categorize and load documents
    docs_by_category = defaultdict(list)

    for md_path in md_files:
        if md_path.name == "categories.json":
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tokens = count_tokens(content)
        category = simple_categorize(md_path.stem, content)

        docs_by_category[category].append({
            "filename": md_path.name,
            "content": content,
            "tokens": tokens
        })

        print(f"  {md_path.name}: {category} ({tokens:,} tokens)")

    print(f"\n✓ Categorized into {len(docs_by_category)} categories")

    # Create buckets
    buckets = []
    bucket_num = 1

    for category, docs in docs_by_category.items():
        print(f"\nCategory: {category} ({len(docs)} documents)")

        # Sort by tokens (largest first)
        docs.sort(key=lambda x: x['tokens'], reverse=True)

        current_bucket = {
            "name": f"bucket_{bucket_num:02d}_{category.replace(' & ', '_').replace(' ', '_').lower()}.md",
            "category": category,
            "tokens": 0,
            "documents": []
        }

        for doc in docs:
            if current_bucket["tokens"] + doc["tokens"] <= max_tokens:
                # Fits in current bucket
                current_bucket["documents"].append(doc)
                current_bucket["tokens"] += doc["tokens"]
            else:
                # Save current bucket and start new one
                if current_bucket["documents"]:
                    buckets.append(current_bucket)
                    bucket_num += 1

                current_bucket = {
                    "name": f"bucket_{bucket_num:02d}_{category.replace(' & ', '_').replace(' ', '_').lower()}.md",
                    "category": category,
                    "tokens": doc["tokens"],
                    "documents": [doc]
                }

        # Save last bucket for category
        if current_bucket["documents"]:
            buckets.append(current_bucket)
            bucket_num += 1

    # Write bucket files
    print(f"\n✓ Created {len(buckets)} buckets\n")

    for bucket in buckets:
        output_path = Path(output_dir) / bucket["name"]

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {bucket['category']}\n\n")
            f.write(f"**Bucket:** {bucket['name']}\n")
            f.write(f"**Token Count:** {bucket['tokens']:,} / 2,000,000\n")
            f.write(f"**Documents:** {len(bucket['documents'])}\n\n")
            f.write("---\n\n")

            for doc in bucket["documents"]:
                f.write(f"## Source: {doc['filename']}\n\n")
                f.write(doc["content"])
                f.write("\n\n---\n\n")

        print(f"  {bucket['name']}: {bucket['tokens']:,} tokens ({len(bucket['documents'])} docs)")

    # Save bucket metadata
    metadata = {
        "total_buckets": len(buckets),
        "total_tokens": sum(b["tokens"] for b in buckets),
        "buckets": [
            {
                "name": b["name"],
                "category": b["category"],
                "tokens": b["tokens"],
                "document_count": len(b["documents"]),
                "utilization": f"{(b['tokens'] / max_tokens * 100):.1f}%"
            }
            for b in buckets
        ]
    }

    with open(Path(output_dir) / "bucket_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✅ Total tokens across all buckets: {metadata['total_tokens']:,}")
    print(f"   Average bucket utilization: {(metadata['total_tokens'] / (len(buckets) * max_tokens) * 100):.1f}%")
    print(f"   Metadata saved to: {output_dir}/bucket_metadata.json")

if __name__ == "__main__":
    create_semantic_buckets()
