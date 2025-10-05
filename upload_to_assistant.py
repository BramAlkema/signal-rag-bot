#!/usr/bin/env python3
"""Upload semantic buckets to OpenAI Assistant knowledge base"""

import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def list_assistants():
    """List all available assistants"""
    try:
        assistants = client.beta.assistants.list()
        return assistants.data
    except Exception as e:
        print(f"Error listing assistants: {e}")
        return []

def create_new_assistant(name="RAG Knowledge Assistant"):
    """Create a new assistant with file search enabled"""
    try:
        assistant = client.beta.assistants.create(
            name=name,
            instructions="You are a helpful assistant with access to a comprehensive knowledge base. Answer questions based on the provided documents.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}]
        )
        print(f"✓ Created new assistant: {assistant.id}")
        return assistant
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None

def upload_files_to_assistant(assistant_id, file_paths):
    """Upload files to assistant's knowledge base using vector store"""
    try:
        # Create a vector store
        vector_store = client.beta.vector_stores.create(
            name="RAG Semantic Buckets"
        )
        print(f"✓ Created vector store: {vector_store.id}")

        # Upload files to vector store
        file_streams = []
        for file_path in file_paths:
            file_streams.append(open(file_path, "rb"))

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams
        )

        # Close file streams
        for stream in file_streams:
            stream.close()

        print(f"✓ Uploaded {len(file_paths)} files to vector store")
        print(f"  Status: {file_batch.status}")
        print(f"  File counts: {file_batch.file_counts}")

        # Update assistant to use this vector store
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
        )

        print(f"✓ Linked vector store to assistant {assistant_id}")
        return vector_store

    except Exception as e:
        print(f"Error uploading files: {e}")
        return None

def upload_buckets(bucket_dir="output", assistant_id=None):
    """Upload all bucket files to an assistant"""

    # Get bucket files
    bucket_files = [f for f in Path(bucket_dir).glob("bucket_*.md")]

    if not bucket_files:
        print("No bucket files found!")
        return

    print(f"Found {len(bucket_files)} bucket files to upload\n")

    # Load metadata
    metadata_path = Path(bucket_dir) / "bucket_metadata.json"
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
            print("Bucket Summary:")
            for bucket in metadata["buckets"]:
                print(f"  - {bucket['name']}: {bucket['tokens']:,} tokens ({bucket['document_count']} docs)")
            print()

    # Choose or create assistant
    if not assistant_id:
        print("No assistant ID provided. Options:")
        print("1. Create a new assistant")
        print("2. Use an existing assistant")

        assistants = list_assistants()
        if assistants:
            print("\nExisting assistants:")
            for i, asst in enumerate(assistants, 1):
                print(f"  {i}. {asst.name} (ID: {asst.id})")

        choice = input("\nEnter choice (1 for new, 2 for existing): ").strip()

        if choice == "1":
            name = input("Assistant name [RAG Knowledge Assistant]: ").strip() or "RAG Knowledge Assistant"
            assistant = create_new_assistant(name)
            if not assistant:
                return
            assistant_id = assistant.id
        elif choice == "2":
            if not assistants:
                print("No existing assistants found. Creating new one...")
                assistant = create_new_assistant()
                if not assistant:
                    return
                assistant_id = assistant.id
            else:
                asst_num = int(input("Enter assistant number: ")) - 1
                assistant_id = assistants[asst_num].id
        else:
            print("Invalid choice")
            return

    print(f"\nUploading to assistant: {assistant_id}")

    # Upload files
    file_paths = [str(f) for f in bucket_files]
    vector_store = upload_files_to_assistant(assistant_id, file_paths)

    if vector_store:
        print(f"\n✅ Successfully uploaded {len(bucket_files)} buckets!")
        print(f"   Assistant ID: {assistant_id}")
        print(f"   Vector Store ID: {vector_store.id}")
        print(f"\n   You can now use this assistant at:")
        print(f"   https://platform.openai.com/playground/assistants?assistant={assistant_id}")

if __name__ == "__main__":
    import sys

    assistant_id = sys.argv[1] if len(sys.argv) > 1 else None
    upload_buckets(assistant_id=assistant_id)
