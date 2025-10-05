# Signal RAG Bot

A Signal messenger chatbot powered by OpenAI Assistant API with RAG (Retrieval-Augmented Generation) knowledge base.

## Features

- 📱 Signal messenger integration via linked device
- 🤖 OpenAI Assistant API with file search
- 📚 668K tokens of knowledge (Frontend/UI + Security/Auth)
- 💬 Conversation history per user
- 🔒 Optional user authorization

## Architecture

1. **PDF Processing Pipeline**: Extract PDFs → Structure preservation (TOC, links, tables) → Semantic bucketing
2. **Knowledge Base**: 2 buckets uploaded to OpenAI Assistant (max 2M tokens each)
3. **Signal Bot**: Linked device mode (no separate phone number needed)

## Setup

### Prerequisites

- Python 3.11+
- signal-cli (installed via Homebrew)
- OpenAI API key
- Signal account

### Installation

```bash
# Install signal-cli
brew install signal-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
OPENAI_API_KEY=your_openai_api_key
SIGNAL_PHONE_NUMBER=your_phone_number
```

2. Link Signal account:
```bash
signal-cli link -n "RAG-Bot"
# Scan QR code with Signal app: Settings → Linked Devices
```

### Upload Knowledge Base

```bash
# Process PDFs and create buckets
python3 download_pdfs.py
python3 extract_structured.py
python3 create_buckets.py

# Upload to OpenAI Assistant
python3 upload_auto.py
# Note the Assistant ID and update signal_bot_linked.py
```

### Run Bot

```bash
source venv/bin/activate
python3 signal_bot_linked.py
```

## Usage

Send messages to "Note to Self" in Signal or have contacts message you.

**Commands:**
- `/help` - Show help message
- `/info` - Knowledge base stats
- `/reset` - Clear conversation history

## Deployment

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for containerized deployment.

## Project Structure

```
.
├── signal_bot_linked.py      # Main bot (linked device mode)
├── download_pdfs.py           # Download PDFs from URLs
├── extract_structured.py      # Extract with structure preservation
├── create_buckets.py          # Semantic bucketing
├── upload_auto.py             # Upload to OpenAI Assistant
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
└── docker-compose.yml         # Orchestration
```

## Knowledge Base Stats

- **Frontend & UI**: 430K tokens (17 docs)
- **Security & Auth**: 238K tokens (2 docs)
- **Total**: 668K tokens

## License

MIT
