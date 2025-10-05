#!/usr/bin/env python3
"""
Create properly structured buckets with:
- Clear category description
- Source index with PDF links
- Proper document attribution
"""
import os
import json
from pathlib import Path
from create_buckets import count_tokens

def load_metadata():
    """Load PDF metadata"""
    with open("pdf_metadata.json", "r") as f:
        return json.load(f)

def get_clean_title(meta):
    """Get clean title for display"""
    title = meta.get('title', '').strip()

    if not title or title in ["PowerPoint-presentatie", "Journal Article"]:
        first_text = meta.get('first_text', '')[:100]
        for line in first_text.split('\n'):
            line = line.strip()
            if len(line) > 10 and not line.isdigit():
                title = line[:80]
                break

    return title or meta['file'].replace('.pdf', '')

def categorize(meta):
    """Categorize based on content"""
    title = meta.get('title', '').lower()
    first_text = meta.get('first_text', '').lower()
    combined = f"{title} {first_text}"

    if any(k in combined for k in ['procurement', 'aanbesteding', 'artikel 346', 'vweu', 'juridisch', 'legal']):
        return "Legal & Procurement"
    if any(k in combined for k in ['drone', 'onbeman', 'unmanned', 'uav', 'uas']):
        return "Drones & Unmanned Systems"
    if any(k in combined for k in ['ecosystem', 'ecosysteem', 'innovatie', 'valley of death', 'entrepreneurial']):
        return "Ecosystems & Innovation"
    if any(k in combined for k in ['strategi', 'policy', 'white paper', 'kamerbrief', 'actieplan']):
        return "Policy & Strategy"
    if any(k in combined for k in ['financier', 'funding', 'investment']):
        return "Financing & Investment"

    return "Defense Industry"

def create_bucket_header(category, docs):
    """Create structured bucket header"""
    header = f"""# {category}

**Knowledge Domain**: Dutch Defense Industry & Policy
**Documents**: {len(docs)}
**Last Updated**: 2025-10-05

---

## About This Bucket

This bucket contains {len(docs)} documents related to **{category}** in the Dutch defense industry context.

### Topics Covered:
"""

    # Extract unique topics from titles
    topics = set()
    for doc in docs:
        title = get_clean_title(doc)
        if 'ecosystem' in title.lower() or 'ecosysteem' in title.lower():
            topics.add("- Entrepreneurial ecosystems")
        if 'drone' in title.lower() or 'onbeman' in title.lower():
            topics.add("- Drones and unmanned systems")
        if 'procurement' in title.lower() or 'aanbesteding' in title.lower():
            topics.add("- Procurement and legal frameworks")
        if any(k in title.lower() for k in ['strategi', 'policy', 'white paper']):
            topics.add("- Defense policy and strategy")
        if 'financier' in title.lower() or 'funding' in title.lower():
            topics.add("- Financing and investment")

    header += '\n'.join(sorted(topics) or ['- General defense industry'])

    header += "\n\n---\n\n## Document Index\n\n"
    header += "| # | Title | Author | Pages | Source PDF |\n"
    header += "|---|-------|--------|-------|------------|\n"

    for i, doc in enumerate(docs, 1):
        title = get_clean_title(doc)
        author = doc.get('author', 'Unknown')[:30]
        pages = doc.get('pages', 0)
        pdf_id = doc['file'].replace('.pdf', '')

        # Create Google Drive link
        drive_link = f"[PDF]({doc['file']})"

        header += f"| {i} | {title[:50]} | {author} | {pages} | {drive_link} |\n"

    header += "\n---\n\n## Content\n\n"
    header += "> **Note**: Each document below includes source attribution. When answering questions, always cite the source document.\n\n"

    return header

def create_buckets():
    """Create properly structured buckets"""
    metadata = load_metadata()

    # Categorize
    categories = {}
    for meta in metadata:
        cat = categorize(meta)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(meta)

    # Sort categories by size (largest first)
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

    output_dir = Path("output_v3")
    output_dir.mkdir(exist_ok=True)

    bucket_files = []

    for category, docs in sorted_cats:
        docs.sort(key=lambda x: get_clean_title(x))

        # Create bucket with header
        bucket_content = create_bucket_header(category, docs)

        # Add document contents
        total_tokens = 0
        for i, doc in enumerate(docs, 1):
            title = get_clean_title(doc)
            pdf_id = doc['file'].replace('.pdf', '')

            # Find corresponding MD file in output
            md_file = Path(f"output/{pdf_id}.md")

            content = ""
            if md_file.exists():
                with open(md_file, 'r') as f:
                    content = f.read()
                tokens = count_tokens(content)
                total_tokens += tokens
            else:
                content = f"[Content not extracted - source: {doc['file']}]"
                tokens = 0

            # Add document section
            bucket_content += f"\n\n## Document {i}: {title}\n\n"
            bucket_content += f"**Source PDF**: `{doc['file']}`  \n"
            if doc.get('title'):
                bucket_content += f"**Original Title**: {doc['title']}  \n"
            if doc.get('author'):
                bucket_content += f"**Author**: {doc['author']}  \n"
            bucket_content += f"**Pages**: {doc['pages']}  \n"
            bucket_content += f"**Tokens**: {tokens:,}  \n\n"
            bucket_content += "---\n\n"
            bucket_content += content
            bucket_content += "\n\n"

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
        print(f"  Category: {category}")
        print(f"  Documents: {len(docs)}")
        print(f"  Tokens: {total_tokens:,}")

    # Create manifest
    manifest = {
        'buckets': bucket_files,
        'total_docs': len(metadata),
        'total_tokens': sum(b['tokens'] for b in bucket_files),
        'categories': [cat for cat, _ in sorted_cats]
    }

    with open(output_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "="*70)
    print("BUCKET CREATION SUMMARY")
    print("="*70)
    print(f"Total buckets: {len(bucket_files)}")
    print(f"Total documents: {len(metadata)}")
    print(f"Total tokens: {manifest['total_tokens']:,}")
    print(f"\nBuckets created in: {output_dir}/")
    print("\nCategories:")
    for cat, docs in sorted_cats:
        print(f"  - {cat}: {len(docs)} docs")

    return bucket_files

if __name__ == "__main__":
    print("🔨 Creating properly structured buckets with source references...\n")
    buckets = create_buckets()
    print("\n✅ Done!")
    print("\nNext step: Review buckets in output_v3/ then upload to Assistant")
