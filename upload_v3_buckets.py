#!/usr/bin/env python3
"""Upload output_v3 buckets to new OpenAI Assistant"""
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Find all bucket files
bucket_dir = Path("output_v3")
bucket_files = sorted(bucket_dir.glob("bucket_*.md"))

print(f"Found {len(bucket_files)} buckets to upload\n")

# Upload files
file_ids = []
for bucket_file in bucket_files:
    print(f"Uploading: {bucket_file.name}")
    with open(bucket_file, "rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
        file_ids.append(uploaded.id)
        print(f"  → File ID: {uploaded.id}")

print(f"\nTotal files uploaded: {len(file_ids)}")

# Create assistant with files
print("\nCreating Assistant with file search...")
assistant = client.beta.assistants.create(
    name="Dutch Defense Industry Knowledge Bot v3",
    instructions="""You are a knowledgeable assistant specializing in Dutch defense industry, policy, and procurement.

Your knowledge base contains documents about:
- Defense procurement and legal frameworks
- Defense industry ecosystems and innovation
- Drones and unmanned systems
- Policy and strategy documents

When answering questions:
1. Always cite the source document (filename and title)
2. Reference specific pages when possible
3. Be precise and factual
4. If information isn't in the knowledge base, say so clearly

The documents are categorized into buckets. Each bucket has a document index at the top showing all sources.""",
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "file_ids": file_ids
        }
    }
)

print(f"\n✅ Assistant created!")
print(f"Assistant ID: {assistant.id}")
print(f"Files attached: {len(file_ids)}")
print(f"\nNext step: Update .env with ASSISTANT_ID={assistant.id}")
print(f"Then restart the bot!")
