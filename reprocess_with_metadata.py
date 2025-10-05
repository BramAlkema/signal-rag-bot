#!/usr/bin/env python3
"""
Re-process PDFs with proper naming based on metadata
Creates new buckets with meaningful names and source attribution
"""
import os
import json
import shutil
from pathlib import Path
from create_buckets import count_tokens

def load_metadata():
    """Load PDF metadata"""
    with open("pdf_metadata.json", "r") as f:
        return json.load(f)

def get_clean_title(meta):
    """Get clean title for filename"""
    title = meta.get('title', '').strip()

    # If no title, extract from first text
    if not title or title == "PowerPoint-presentatie":
        first_text = meta.get('first_text', '')[:100]
        # Take first meaningful line
        for line in first_text.split('\n'):
            line = line.strip()
            if len(line) > 10 and not line.isdigit():
                title = line[:60]
                break

    # Clean for filename
    title = title.replace('/', '-').replace('\\', '-')
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        title = title.replace(char, '')

    return title[:80]  # Limit length

def categorize_by_metadata(meta):
    """Categorize based on metadata analysis"""
    title = meta.get('title', '').lower()
    first_text = meta.get('first_text', '').lower()
    combined = f"{title} {first_text}"

    # Legal/Procurement keywords
    if any(k in combined for k in ['procurement', 'aanbesteding', 'artikel 346', 'vweu', 'tfeu', 'juridisch', 'legal']):
        return "Legal & Procurement"

    # Drone/Unmanned systems
    if any(k in combined for k in ['drone', 'onbeman', 'unmanned', 'uav', 'uas']):
        return "Drones & Unmanned Systems"

    # Ecosystem/Innovation
    if any(k in combined for k in ['ecosystem', 'ecosysteem', 'innovatie', 'valley of death', 'entrepreneurial']):
        return "Ecosystems & Innovation"

    # Policy/Strategy
    if any(k in combined for k in ['strategi', 'policy', 'white paper', 'kamerbrief', 'actieplan']):
        return "Policy & Strategy"

    # Financing
    if any(k in combined for k in ['financier', 'funding', 'investment']):
        return "Financing & Investment"

    return "General Defense Industry"

def create_improved_buckets():
    """Create new buckets with metadata-based naming"""
    metadata = load_metadata()

    # Categorize all PDFs
    categories = {}
    for meta in metadata:
        category = categorize_by_metadata(meta)
        if category not in categories:
            categories[category] = []
        categories[category].append(meta)

    # Print categorization summary
    print("\n" + "="*70)
    print("CATEGORIZATION SUMMARY")
    print("="*70)
    for cat, docs in categories.items():
        print(f"\n{cat}: {len(docs)} documents")
        for doc in docs:
            title = get_clean_title(doc)
            print(f"  - {doc['file'][:30]}... → {title[:50]}")

    # Create buckets
    output_dir = Path("output_v2")
    output_dir.mkdir(exist_ok=True)

    bucket_files = []

    for category, docs in categories.items():
        # Sort by title for consistency
        docs.sort(key=lambda x: get_clean_title(x))

        # Create bucket content
        bucket_content = f"# {category}\n\n"
        bucket_content += f"**Category**: {category}  \n"
        bucket_content += f"**Documents**: {len(docs)}  \n"
        bucket_content += f"**Topic**: Dutch Defense Industry Knowledge Base\n\n"
        bucket_content += "---\n\n"
        bucket_content += "## Documents in this bucket:\n\n"

        for i, doc in enumerate(docs, 1):
            title = get_clean_title(doc)
            bucket_content += f"{i}. **{title}** ({doc['pages']} pages)\n"
            if doc.get('author'):
                bucket_content += f"   - Author: {doc['author']}\n"
            bucket_content += f"   - Source: {doc['file']}\n\n"

        bucket_content += "\n---\n\n## Content\n\n"

        # Add extracted content
        total_tokens = 0
        for doc in docs:
            file_id = doc['file'].replace('.pdf', '')
            md_path = Path(f"output/{file_id}.md")

            if md_path.exists():
                with open(md_path, 'r') as f:
                    content = f.read()

                title = get_clean_title(doc)
                bucket_content += f"\n## {title}\n\n"
                bucket_content += f"**Source**: {doc['file']}  \n"
                if doc.get('title'):
                    bucket_content += f"**Original Title**: {doc['title']}  \n"
                if doc.get('author'):
                    bucket_content += f"**Author**: {doc['author']}  \n"
                bucket_content += f"**Pages**: {doc['pages']}\n\n"
                bucket_content += content + "\n\n"

                total_tokens += count_tokens(content)

        # Save bucket
        safe_cat = category.replace(' & ', '_').replace(' ', '_').lower()
        bucket_file = output_dir / f"bucket_{safe_cat}.md"

        with open(bucket_file, 'w') as f:
            f.write(bucket_content)

        bucket_files.append({
            'file': str(bucket_file),
            'category': category,
            'docs': len(docs),
            'tokens': total_tokens
        })

        print(f"\n✓ Created: {bucket_file.name}")
        print(f"  Documents: {len(docs)}")
        print(f"  Tokens: {total_tokens:,}")

    # Save manifest
    manifest = {
        'buckets': bucket_files,
        'total_docs': len(metadata),
        'total_tokens': sum(b['tokens'] for b in bucket_files),
        'categories': list(categories.keys())
    }

    with open(output_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total buckets: {len(bucket_files)}")
    print(f"Total documents: {len(metadata)}")
    print(f"Total tokens: {manifest['total_tokens']:,}")
    print(f"\nOutput directory: {output_dir}/")

    return bucket_files

if __name__ == "__main__":
    print("🔄 Re-processing PDFs with metadata-based categorization...")
    bucket_files = create_improved_buckets()
    print("\n✅ Done!")
    print("\nNext steps:")
    print("1. Review buckets in output_v2/")
    print("2. Run upload_auto.py to create new assistant")
    print("3. Update signal_bot_linked.py with new ASSISTANT_ID")
