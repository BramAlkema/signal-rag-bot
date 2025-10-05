# Signal RAG Chatbot Setup Guide

## What This Does

Creates a **Signal messenger chatbot** that answers questions using your RAG knowledge base (668K tokens from 19 PDFs).

## Prerequisites

### 1. Install signal-cli

```bash
# macOS
brew install signal-cli

# Linux (Debian/Ubuntu)
sudo apt install signal-cli

# Or download from: https://github.com/AsamK/signal-cli
```

### 2. Register Your Signal Number

You need a **separate phone number** for the bot (cannot use your personal Signal number).

```bash
# Replace with your bot's phone number
export SIGNAL_PHONE_NUMBER="+1234567890"

# Register
signal-cli -u $SIGNAL_PHONE_NUMBER register

# You'll receive an SMS with a verification code
signal-cli -u $SIGNAL_PHONE_NUMBER verify CODE_FROM_SMS
```

### 3. Set Environment Variables

```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-proj-..."
export SIGNAL_PHONE_NUMBER="+1234567890"
```

## Running the Bot

### Option 1: Direct Run

```bash
cd /Users/ynse/projects/RAG
source venv/bin/activate
python3 signal_bot.py
```

### Option 2: Background Service

```bash
# Run in background
nohup python3 signal_bot.py > signal_bot.log 2>&1 &

# Check logs
tail -f signal_bot.log

# Stop
pkill -f signal_bot.py
```

## How to Use

### Send a Message to Your Bot

1. Open Signal on your phone
2. Start a new conversation with your bot's number
3. Send a message like:
   - "How do I implement authentication?"
   - "Explain React components best practices"
   - "What security measures should I use?"

### Bot Commands

- `/help` - Show available commands
- `/info` - Show knowledge base statistics
- `/reset` - Clear conversation history (start fresh)

## Features

✅ **Persistent conversations** - Bot remembers context per user
✅ **Multi-user support** - Different users get separate conversation threads
✅ **RAG knowledge base** - 668K tokens of documentation
✅ **Automatic polling** - Checks for new messages every 5 seconds

## Troubleshooting

### "signal-cli not found"
```bash
brew install signal-cli
```

### "Unable to send message"
Make sure you've registered and verified your number:
```bash
signal-cli -u $SIGNAL_PHONE_NUMBER receive
```

### "OpenAI quota exceeded"
You need to add credits to your OpenAI account:
https://platform.openai.com/account/billing

### "Assistant not responding"
The files might not be attached to the assistant. Go to:
https://platform.openai.com/playground/assistants?assistant=asst_wnQHRKjNOMDggxCAYLgymW4w

And manually attach the uploaded files.

## Architecture

```
Signal User → signal-cli → signal_bot.py → OpenAI Assistant API → RAG Buckets
                                                ↓
                                            Response
                                                ↓
Signal User ← signal-cli ← signal_bot.py ← OpenAI Assistant API
```

## Cost Estimates

- **Signal**: Free (uses your phone number)
- **OpenAI API**:
  - GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
  - Average conversation: ~$0.01-0.05 per exchange

## Next Steps

1. **Test locally** first with one user
2. **Monitor logs** to see how it performs
3. **Improve prompts** in the assistant configuration
4. **Add more knowledge** by processing more PDFs
5. **Deploy to a server** for 24/7 uptime

## File Locations

- Bot script: `/Users/ynse/projects/RAG/signal_bot.py`
- Knowledge buckets: `/Users/ynse/projects/RAG/output/`
- Assistant ID: `asst_wnQHRKjNOMDggxCAYLgymW4w`
