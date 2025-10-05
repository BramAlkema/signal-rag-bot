#!/usr/bin/env python3
"""
Signal RAG Bot using signalbot library (easier than raw signal-cli)

Install:
    pip install signalbot

Still needs signal-cli installed, but signalbot makes it much easier!
"""

import os
from signalbot import SignalBot, Command, Context
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SIGNAL_PHONE_NUMBER = os.environ.get("SIGNAL_PHONE_NUMBER", "+YOUR_NUMBER")
ASSISTANT_ID = "asst_5eRxLWftGiZttJNSEWMO7MuU"

client = OpenAI(api_key=OPENAI_API_KEY)
user_threads = {}

class RAGBot(SignalBot):
    """Signal bot with RAG knowledge base"""

    def get_assistant_response(self, user_message: str, sender: str) -> str:
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
            import time
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
            return f"Error: {str(e)}"

    async def default(self, context: Context):
        """Handle all messages"""
        message = context.message.text
        sender = context.message.source

        print(f"📨 {sender}: {message}")

        # Get AI response
        response = self.get_assistant_response(message, sender)

        # Send reply
        await context.send(response)

# Commands
class ResetCommand(Command):
    """Reset conversation history"""

    async def handle(self, context: Context):
        sender = context.message.source
        if sender in user_threads:
            del user_threads[sender]
        await context.send("✅ Conversation reset!")

class InfoCommand(Command):
    """Show knowledge base info"""

    async def handle(self, context: Context):
        info = """📚 RAG Knowledge Base

• Frontend & UI: 430K tokens
• Security & Auth: 238K tokens

Total: 668K tokens of docs

Commands:
/info - This message
/reset - Clear history"""
        await context.send(info)

if __name__ == "__main__":
    # Create bot
    bot = RAGBot(
        phone_number=SIGNAL_PHONE_NUMBER,
        # Optional: specify signal-cli path if not in PATH
        # signal_service=SignalAPI(...)
    )

    # Register commands
    bot.register_command(ResetCommand("/reset"))
    bot.register_command(InfoCommand("/info"))

    print("=" * 70)
    print("🤖 Signal RAG Bot (using signalbot library)")
    print("=" * 70)
    print(f"Phone: {SIGNAL_PHONE_NUMBER}")
    print(f"Assistant: {ASSISTANT_ID}")
    print("\n🔄 Starting bot...\n")

    # Start bot
    bot.start()
