#!/usr/bin/env python3
"""
Signal Chatbot using LINKED DEVICE (no separate number needed!)

This links signal-cli to your existing Signal account as a secondary device,
like Signal Desktop. Your main Signal app keeps working!

Setup:
1. Install signal-cli: brew install signal-cli
2. Link as device: signal-cli link -n "RAG-Bot"
3. Scan QR code with your Signal app (Settings → Linked Devices)
4. Run this bot!
"""

import os
import json
import subprocess
import time
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ASSISTANT_ID = os.environ.get("ASSISTANT_ID", "asst_5eRxLWftGiZttJNSEWMO7MuU")

# Authorized users (phone numbers that can use the bot)
# Leave empty [] to allow anyone, or add specific numbers like ["+1234567890"]
AUTHORIZED_USERS = []

client = OpenAI(api_key=OPENAI_API_KEY)
user_threads = {}

def send_signal_message(recipient, message):
    """Send message via signal-cli (linked device mode)"""
    try:
        # In linked mode, we don't specify -u (it uses linked account)
        cmd = [
            "signal-cli",
            "send",
            "-m", message,
            recipient
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Sent to {recipient}: {message[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to send: {e}")
        return False

def receive_signal_messages():
    """Receive messages from Signal (linked device mode)"""
    try:
        cmd = ["signal-cli", "-o", "json", "receive", "-t", "2"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        messages = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    # Skip log lines that aren't JSON
                    if not line.startswith('{'):
                        continue

                    msg = json.loads(line)
                    envelope = msg.get('envelope', {})
                    sender = envelope.get('source')
                    text = None

                    # Check for regular data message
                    if envelope.get('dataMessage'):
                        text = envelope['dataMessage'].get('message', '')

                    # Check for sync message (Note to Self)
                    elif envelope.get('syncMessage', {}).get('sentMessage'):
                        sent = envelope['syncMessage']['sentMessage']
                        text = sent.get('message', '')

                    if text and sender:
                        # Check authorization
                        if AUTHORIZED_USERS and sender not in AUTHORIZED_USERS:
                            print(f"⚠️  Unauthorized user: {sender}")
                            continue

                        messages.append({
                            'sender': sender,
                            'text': text,
                            'timestamp': envelope.get('timestamp')
                        })
                except (json.JSONDecodeError, KeyError):
                    continue

        return messages
    except Exception as e:
        print(f"✗ Failed to receive: {e}")
        return []

def get_assistant_response(user_message, sender):
    """Get response from OpenAI Assistant"""

    # Get or create thread for this user
    if sender not in user_threads:
        thread = client.beta.threads.create()
        user_threads[sender] = thread.id

    thread_id = user_threads[sender]

    try:
        # Add user message
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
        for _ in range(30):
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "expired", "cancelled"]:
                return f"Error: {run_status.status}"

            time.sleep(2)

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)

        if messages.data and messages.data[0].role == "assistant":
            return messages.data[0].content[0].text.value

        return "Sorry, couldn't generate response."

    except Exception as e:
        print(f"✗ Assistant error: {e}")
        return f"Error: {str(e)}"

def process_messages():
    """Main message processing loop"""
    print("=" * 70)
    print("📱 Signal RAG Bot (Linked Device Mode)")
    print("=" * 70)
    print(f"Assistant ID: {ASSISTANT_ID}")
    print(f"Knowledge: 668K tokens (Frontend/UI + Security/Auth)")
    if AUTHORIZED_USERS:
        print(f"Authorized users: {', '.join(AUTHORIZED_USERS)}")
    else:
        print("⚠️  Open to all users (set AUTHORIZED_USERS to restrict)")
    print("\n🔄 Listening for messages...\n")

    while True:
        try:
            messages = receive_signal_messages()

            for msg in messages:
                sender = msg['sender']
                text = msg['text']

                if not text:
                    continue

                print(f"\n📨 {sender}: {text}")

                # Commands
                if text.lower() == "/reset":
                    if sender in user_threads:
                        del user_threads[sender]
                    send_signal_message(sender, "✅ Conversation reset!")
                    continue

                if text.lower() == "/help":
                    help_msg = """🤖 RAG Knowledge Bot

Commands:
/help - Show this message
/reset - Clear history
/info - Knowledge base stats

Ask me about:
• Frontend & UI Development
• Security & Authentication

I have 668K tokens of docs!"""
                    send_signal_message(sender, help_msg)
                    continue

                if text.lower() == "/info":
                    info_msg = """📚 Knowledge Base

• Frontend & UI: 430K tokens
• Security & Auth: 238K tokens
Total: 668K tokens"""
                    send_signal_message(sender, info_msg)
                    continue

                # Get AI response
                print("🤔 Thinking...")
                response = get_assistant_response(text, sender)
                send_signal_message(sender, response)

            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(10)

def setup_linked_device():
    """Guide user through linking process"""
    print("\n" + "=" * 70)
    print("🔗 Signal Linked Device Setup")
    print("=" * 70)
    print("\nThis will link signal-cli to your existing Signal account.")
    print("Your main Signal app will keep working!\n")
    print("Steps:")
    print("1. Run: signal-cli link -n 'RAG-Bot'")
    print("2. Scan the QR code with your Signal app:")
    print("   Settings → Linked Devices → Link New Device")
    print("3. Come back here and run the bot again\n")
    print("=" * 70 + "\n")

def check_linked_status():
    """Check if signal-cli is linked"""
    try:
        result = subprocess.run(
            ["signal-cli", "receive"],
            capture_output=True,
            text=True,
            timeout=2
        )
        # If it doesn't error about not being registered, we're linked
        return True
    except subprocess.TimeoutExpired:
        return True  # Timeout means it's waiting for messages (linked)
    except:
        return False

def main():
    """Main entry point"""

    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set!")
        return

    # Check signal-cli
    try:
        subprocess.run(["signal-cli", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        print("❌ signal-cli not installed!")
        print("   Install: brew install signal-cli")
        return

    # Check if linked
    if not check_linked_status():
        setup_linked_device()
        return

    # Start bot
    process_messages()

if __name__ == "__main__":
    main()
