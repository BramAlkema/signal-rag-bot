#!/usr/bin/env python3
"""
Signal Chatbot with RAG Knowledge Base
Based on: https://github.com/piebro/signal-ai-chat-bot

Requirements:
1. signal-cli installed and configured
2. OpenAI API key in environment
3. Your bucket files uploaded to OpenAI Assistant
"""

import os
import json
import subprocess
import time
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SIGNAL_PHONE_NUMBER = os.environ.get("SIGNAL_PHONE_NUMBER")  # Your Signal number (e.g., +1234567890)
ASSISTANT_ID = "asst_wnQHRKjNOMDggxCAYLgymW4w"  # Your uploaded assistant

client = OpenAI(api_key=OPENAI_API_KEY)

# Store conversation threads per user
user_threads = {}

def send_signal_message(recipient, message):
    """Send a message via Signal using signal-cli"""
    try:
        cmd = [
            "signal-cli",
            "-u", SIGNAL_PHONE_NUMBER,
            "send",
            "-m", message,
            recipient
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Sent to {recipient}: {message[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to send Signal message: {e}")
        return False

def receive_signal_messages():
    """Receive messages from Signal using signal-cli"""
    try:
        cmd = [
            "signal-cli",
            "-u", SIGNAL_PHONE_NUMBER,
            "receive",
            "--json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        messages = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    msg = json.loads(line)
                    if msg.get('envelope', {}).get('dataMessage'):
                        messages.append({
                            'sender': msg['envelope']['source'],
                            'text': msg['envelope']['dataMessage'].get('message', ''),
                            'timestamp': msg['envelope']['timestamp']
                        })
                except json.JSONDecodeError:
                    continue

        return messages
    except Exception as e:
        print(f"✗ Failed to receive Signal messages: {e}")
        return []

def get_assistant_response(user_message, sender):
    """Get response from OpenAI Assistant with RAG knowledge"""

    # Get or create thread for this user
    if sender not in user_threads:
        thread = client.beta.threads.create()
        user_threads[sender] = thread.id

    thread_id = user_threads[sender]

    try:
        # Add user message to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for completion
        max_attempts = 30
        for _ in range(max_attempts):
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "expired", "cancelled"]:
                return f"Sorry, I encountered an error: {run_status.status}"

            time.sleep(2)

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)

        if messages.data:
            assistant_message = messages.data[0]
            if assistant_message.role == "assistant":
                return assistant_message.content[0].text.value

        return "Sorry, I couldn't generate a response."

    except Exception as e:
        print(f"✗ Assistant error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def process_messages():
    """Main message processing loop"""
    print("📱 Signal RAG Chatbot Started")
    print(f"   Assistant ID: {ASSISTANT_ID}")
    print(f"   Signal Number: {SIGNAL_PHONE_NUMBER}")
    print("\n🔄 Listening for messages...\n")

    while True:
        try:
            # Receive new messages
            messages = receive_signal_messages()

            for msg in messages:
                sender = msg['sender']
                text = msg['text']

                if not text:
                    continue

                print(f"\n📨 From {sender}: {text}")

                # Special commands
                if text.lower() == "/reset":
                    if sender in user_threads:
                        del user_threads[sender]
                    send_signal_message(sender, "✅ Conversation history reset!")
                    continue

                if text.lower() == "/help":
                    help_text = """🤖 RAG Knowledge Assistant

Available commands:
/help - Show this help
/reset - Clear conversation history
/info - Show knowledge base info

Ask me anything about:
• Frontend & UI Development
• Security & Authentication

I have access to 668K tokens of documentation!"""
                    send_signal_message(sender, help_text)
                    continue

                if text.lower() == "/info":
                    info_text = """📚 Knowledge Base Info

Buckets:
• Frontend & UI: 430K tokens (17 docs)
• Security & Auth: 238K tokens (2 docs)

Total: 668K tokens of documentation"""
                    send_signal_message(sender, info_text)
                    continue

                # Get AI response
                print("🤔 Thinking...")
                response = get_assistant_response(text, sender)

                # Send response
                send_signal_message(sender, response)

            # Poll every 5 seconds
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            time.sleep(10)

def check_requirements():
    """Check if signal-cli is installed and configured"""
    try:
        result = subprocess.run(
            ["signal-cli", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ signal-cli version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ signal-cli not found!")
        print("\nInstall it:")
        print("  brew install signal-cli")
        print("\nThen register your number:")
        print(f"  signal-cli -u {SIGNAL_PHONE_NUMBER or '+YOUR_NUMBER'} register")
        print(f"  signal-cli -u {SIGNAL_PHONE_NUMBER or '+YOUR_NUMBER'} verify CODE")
        return False
    except Exception as e:
        print(f"❌ Error checking signal-cli: {e}")
        return False

def main():
    """Main entry point"""

    # Check environment
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set!")
        return

    if not SIGNAL_PHONE_NUMBER:
        print("❌ SIGNAL_PHONE_NUMBER not set!")
        print("   Set it: export SIGNAL_PHONE_NUMBER='+1234567890'")
        return

    # Check signal-cli
    if not check_requirements():
        return

    # Start bot
    process_messages()

if __name__ == "__main__":
    main()
