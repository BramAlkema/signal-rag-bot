#!/usr/bin/env python3
"""Auto-upload semantic buckets to new OpenAI Assistant"""

import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def main():
    bucket_dir = "output"
    bucket_files = sorted(Path(bucket_dir).glob("bucket_*.md"))

    if not bucket_files:
        print("❌ No bucket files found!")
        return

    print(f"📦 Found {len(bucket_files)} bucket files\n")

    # Load metadata
    with open(Path(bucket_dir) / "bucket_metadata.json") as f:
        metadata = json.load(f)
        for bucket in metadata["buckets"]:
            print(f"  • {bucket['name']}: {bucket['tokens']:,} tokens ({bucket['document_count']} docs)")

    print(f"\n📊 Total: {metadata['total_tokens']:,} tokens across {len(bucket_files)} buckets\n")

    # Create assistant
    print("🤖 Creating new assistant...")
    try:
        assistant = client.beta.assistants.create(
            name="RAG Knowledge Assistant",
            instructions="You are a helpful assistant with access to a comprehensive knowledge base. Answer questions based on the provided documents.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}]
        )
        print(f"✅ Created assistant: {assistant.id}\n")
    except Exception as e:
        print(f"❌ Failed to create assistant: {e}")
        return

    # Upload files to OpenAI
    print(f"⬆️  Uploading {len(bucket_files)} bucket files...")
    file_ids = []
    try:
        for bucket_file in bucket_files:
            with open(bucket_file, "rb") as f:
                uploaded_file = client.files.create(
                    file=f,
                    purpose="assistants"
                )
                file_ids.append(uploaded_file.id)
                print(f"   ✓ {bucket_file.name}: {uploaded_file.id}")

        print(f"✅ Uploaded {len(file_ids)} files\n")
    except Exception as e:
        print(f"❌ Failed to upload files: {e}")
        return

    # Attach files to assistant
    print("🔗 Attaching files to assistant...")
    try:
        client.beta.assistants.update(
            assistant_id=assistant.id,
            file_ids=file_ids
        )
        print(f"✅ Attached {len(file_ids)} files!\n")
    except Exception as e:
        print(f"❌ Failed to attach files: {e}")
        print(f"   Note: Files were uploaded with IDs: {file_ids}")
        print(f"   You can manually attach them to assistant: {assistant.id}")
        return

    # Success!
    print("=" * 60)
    print("🎉 SUCCESS! Your knowledge base is ready!")
    print("=" * 60)
    print(f"\n📋 Assistant ID: {assistant.id}")
    print(f"📋 File IDs: {', '.join(file_ids)}")
    print(f"\n🌐 Test it here:")
    print(f"   https://platform.openai.com/playground/assistants?assistant={assistant.id}")
    print(f"\n💡 Or use it via API with assistant ID: {assistant.id}")

if __name__ == "__main__":
    main()
