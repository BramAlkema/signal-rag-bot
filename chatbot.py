#!/usr/bin/env python3
"""Simple chatbot that answers questions using the RAG Assistant"""

import os
import time
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Your assistant ID (from the upload)
ASSISTANT_ID = "asst_wnQHRKjNOMDggxCAYLgymW4w"

# File IDs of your uploaded buckets
FILE_IDS = [
    "file-NTHHNLaGJTPUDcDo44eZSx",  # bucket_01_frontend_ui.md
    "file-2ijNiDAimcRtYkYfhoGxSu"   # bucket_02_security_auth.md
]

def create_vector_store_and_attach():
    """Create vector store and attach files to assistant"""
    print("🔧 Setting up vector store...")

    try:
        # Create vector store
        vector_store = client.beta.vector_stores.create(
            name="RAG Knowledge Base",
            file_ids=FILE_IDS
        )
        print(f"✅ Created vector store: {vector_store.id}")

        # Wait for files to be processed
        print("⏳ Processing files...")
        while True:
            vs = client.beta.vector_stores.retrieve(vector_store.id)
            if vs.status == "completed":
                print("✅ Files processed!")
                break
            elif vs.status == "failed":
                print("❌ File processing failed")
                return None
            time.sleep(2)

        # Attach to assistant
        client.beta.assistants.update(
            assistant_id=ASSISTANT_ID,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        print(f"✅ Attached vector store to assistant\n")
        return vector_store.id

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("You may need to manually attach files in the OpenAI Playground")
        return None

def chat(question, thread_id=None):
    """Ask a question to the assistant"""

    # Create or use existing thread
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Add message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    # Wait for completion
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            return None, thread_id, "Error: Assistant run failed"

        time.sleep(1)

    # Get the response
    messages = client.beta.threads.messages.list(thread_id=thread_id)

    # Get the latest assistant message
    for message in messages.data:
        if message.role == "assistant":
            return message.content[0].text.value, thread_id, None

    return None, thread_id, "No response"

def interactive_chat():
    """Interactive chatbot loop"""
    print("=" * 70)
    print("🤖 RAG Knowledge Assistant Chatbot")
    print("=" * 70)
    print("\nKnowledge Base:")
    print("  • Frontend & UI Development (430K tokens)")
    print("  • Security & Authentication (238K tokens)")
    print("\nType your questions below. Type 'quit' or 'exit' to end.\n")
    print("-" * 70)

    thread_id = None

    while True:
        try:
            question = input("\n💬 You: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not question:
                continue

            print("\n🤔 Assistant is thinking...")

            answer, thread_id, error = chat(question, thread_id)

            if error:
                print(f"\n❌ {error}")
            elif answer:
                print(f"\n🤖 Assistant:\n{answer}")
            else:
                print("\n❌ No response received")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""

    # Option to setup vector store first
    print("\nDo you need to setup the vector store? (y/n)")
    print("(Only needed once, or if files aren't attached)")
    setup = input("> ").strip().lower()

    if setup == 'y':
        create_vector_store_and_attach()

    # Start chat
    interactive_chat()

if __name__ == "__main__":
    main()
