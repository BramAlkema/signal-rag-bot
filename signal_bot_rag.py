#!/usr/bin/env python3
"""
Signal RAG Bot using custom vector store
No OpenAI Assistants API - direct Chat Completions with RAG
Now with production-grade security controls
"""
import os
import json
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Auto-configure for Replit if detected
try:
    from replit_helper import is_replit, configure_for_replit
    if is_replit():
        configure_for_replit()
except ImportError:
    pass  # Not on Replit or helper not available

from custom_rag import CustomRAG
from security import (
    sanitize_message,
    RateLimiter,
    SecretManager,
    ThreatDetector,
    create_safe_prompt,
    CircuitBreaker
)

# Load environment variables
load_dotenv()

# Configuration - use SecretManager for validation
SIGNAL_PHONE_NUMBER = SecretManager.get_secret("SIGNAL_PHONE_NUMBER", required=True)
OPENAI_API_KEY = SecretManager.get_secret("OPENAI_API_KEY", required=True)
AUTHORIZED_USERS = []  # Empty = allow all
ACTIVATION_PASSPHRASE = SecretManager.get_secret("ACTIVATION_PASSPHRASE", required=False) or "Activate Oracle"

# Load PDF URL mapping
PDF_URLS = {}
if Path("pdf_url_mapping.json").exists():
    with open("pdf_url_mapping.json", "r") as f:
        PDF_URLS = json.load(f)

# Initialize RAG
print("🔍 Loading RAG index...")
rag = CustomRAG()
rag.load_index()
print(f"✅ RAG ready with {rag.index.ntotal} chunks\n")

# Initialize security controls
rate_limiter = RateLimiter()
threat_detector = ThreatDetector()
openai_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

# Track conversations and activated users
user_conversations = {}
activated_users = set()  # Users who have said the passphrase

def send_signal_message(recipient, message, preview_url=None):
    """Send message via signal-cli with optional link preview"""
    try:
        cmd = ["signal-cli", "send", "-m", message, recipient]

        # Add link preview if URL provided
        if preview_url:
            cmd.extend([
                "--preview-url", preview_url,
                "--preview-title", "Source Document"
            ])

        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Sent to {recipient}: {message[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to send: {e}")
        return False

def receive_signal_messages():
    """Receive messages from Signal"""
    try:
        cmd = ["signal-cli", "-o", "json", "receive", "-t", "2"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        messages = []
        for line in result.stdout.strip().split('\n'):
            if line and line.startswith('{'):
                try:
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

def get_rag_response(user_message, sender):
    """Get response using custom RAG with security controls"""
    try:
        # SECURITY: Sanitize input
        try:
            user_message = sanitize_message(user_message)
        except ValueError as e:
            return f"❌ Invalid input: {str(e)}"

        # SECURITY: Check for suspicious patterns
        is_suspicious, reason = threat_detector.is_suspicious(user_message)
        if is_suspicious:
            print(f"⚠️  Suspicious input detected from {sender}: {reason}")
            return "⚠️ Your message contains suspicious patterns. Please rephrase your question."

        # Get conversation history
        if sender not in user_conversations:
            user_conversations[sender] = []

        # Add user message to history
        user_conversations[sender].append({
            "role": "user",
            "content": user_message
        })

        # Keep only last 5 messages for context
        recent_history = user_conversations[sender][-5:]

        # Build context with history
        history_context = "\n".join([
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in recent_history[:-1]  # Exclude current message
        ])

        # Get RAG response with history context
        if history_context:
            enhanced_query = f"Previous conversation:\n{history_context}\n\nCurrent question: {user_message}"
        else:
            enhanced_query = user_message

        # Get search results first
        search_results = rag.search(user_message, k=3)

        # Build context
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"[Source {i}: {result['source']}, {result['category']}]\n{result['text']}\n")

        context = "\n---\n".join(context_parts)

        # SECURITY: Use hardened prompt
        prompt = create_safe_prompt(user_message, context)

        # Get response from OpenAI with circuit breaker
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        def call_openai():
            return client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Keep answers concise (2-3 sentences) unless asked for details."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

        # Use circuit breaker to protect against repeated API failures
        try:
            response = openai_circuit_breaker.call(call_openai)
        except Exception as e:
            if "Circuit breaker OPEN" in str(e):
                return "⚠️ Service temporarily unavailable. Please try again in a minute."
            raise e

        answer = response.choices[0].message.content

        # Extract unique PDF files from search results and add Google Drive links
        pdf_files = set()
        for result in search_results:
            chunk_text = result.get('text', '')
            # Look for "**Source PDF**: `filename.pdf`" pattern
            import re
            pdf_matches = re.findall(r'\*\*Source PDF\*\*:\s*`([^`]+\.pdf)`', chunk_text)
            for pdf_name in pdf_matches:
                if pdf_name in PDF_URLS:
                    pdf_files.add((pdf_name, PDF_URLS[pdf_name]))

        if pdf_files:
            answer += "\n\n📄 Source Documents:\n"
            for pdf_name, url in sorted(pdf_files):
                # Signal auto-links plain URLs
                answer += f"{url}\n"

        # Add response to history
        user_conversations[sender].append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:
        print(f"✗ RAG error: {e}")
        return f"Error: {str(e)}"

def process_messages():
    """Main message processing loop"""
    print("="*70)
    print("📱 Signal RAG Bot (Custom Vector Store)")
    print("="*70)
    print(f"Phone: {SIGNAL_PHONE_NUMBER}")
    print(f"Knowledge: 668K tokens (5 buckets, 3240 chunks)")
    if AUTHORIZED_USERS:
        print(f"Authorized users: {', '.join(AUTHORIZED_USERS)}")
    else:
        print("⚠️  Open to all users")
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

                # Check for activation passphrase
                if text.strip() == ACTIVATION_PASSPHRASE:
                    activated_users.add(sender)
                    welcome_msg = """✅ Oracle activated!

Ask me about:
• Dutch defense industry & ecosystems
• Defense procurement & legal frameworks
• Drones & unmanned systems
• Policy & strategy documents

Commands: /help /info /reset"""
                    send_signal_message(sender, welcome_msg)
                    continue

                # Ignore messages from non-activated users (silent)
                if sender not in activated_users:
                    print(f"  ⚠️  Ignoring message from non-activated user: {sender}")
                    continue

                # SECURITY: Check rate limits
                if not rate_limiter.check_rate_limit(sender):
                    print(f"  ⚠️  Rate limit exceeded for {sender}")
                    send_signal_message(sender, "⚠️ Rate limit exceeded. Please slow down (max 10 messages/min, 100/hour).")
                    continue

                # Commands
                if text.lower() == "/reset":
                    if sender in user_conversations:
                        del user_conversations[sender]
                    send_signal_message(sender, "✅ Conversation reset!")
                    continue

                if text.lower() == "/help":
                    help_msg = """🤖 RAG Knowledge Bot

Commands:
/help - Show this message
/reset - Clear history
/info - Knowledge base stats

Ask me about:
• Dutch defense industry & ecosystems
• Defense procurement & legal frameworks
• Drones & unmanned systems
• Policy & strategy documents

I have 668K tokens across 3240 searchable chunks!"""
                    send_signal_message(sender, help_msg)
                    continue

                if text.lower() == "/info":
                    info_msg = f"""📚 Knowledge Base Stats

• Chunks: 3,240
• Total tokens: 668K
• Categories: 5
  - Ecosystems & Innovation
  - Defense Industry
  - Legal & Procurement
  - Policy & Strategy
  - Drones & Unmanned Systems

Custom RAG with FAISS vector store"""
                    send_signal_message(sender, info_msg)
                    continue

                # Get RAG response
                print("🤔 Thinking...")
                response = get_rag_response(text, sender)
                send_signal_message(sender, response)

            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    process_messages()
