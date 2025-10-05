# Signal RAG Bot

A Signal messenger chatbot powered by OpenAI Assistant API with RAG (Retrieval-Augmented Generation) knowledge base.

📚 **[View Project Website](https://bramalkem.github.io/signal-rag-bot/)** | 📖 [Documentation](#documentation) | 🚀 [Quick Deploy](#deployment-options)

> **Note**: This is an MVP demonstrating the RAG pipeline. The semantic bucketing is automated and you can customize categories based on your PDFs.

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

## Deployment Options

Choose the best deployment for your needs:

| Platform | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| **[Replit Free](README_REPLIT.md)** | $0/mo | 5 min | Testing, personal use |
| **[VPS Lite](README_SMALL_BOXES.md)** | $3-6/mo | 15 min | Small teams, budget production |
| **[VPS Standard](DOCKER_DEPLOYMENT.md)** | $12-18/mo | 20 min | Production, high traffic |

📊 **[Compare All Options](DEPLOYMENT_OPTIONS.md)** | 🔄 **[Migration Guide](DEPLOYMENT_COMPARISON.md)**

### Quick Deploy

**Replit (Free)**
```bash
# 1. Import to Replit
# 2. Add secrets, run: bash setup_replit.sh
# 3. Click Run
```

**VPS Lite ($3-6/mo)**
```bash
git clone https://github.com/BramAlkema/signal-rag-bot
cd signal-rag-bot
cp .env.lite .env && nano .env
docker-compose -f docker-compose.lite.yml up -d
```

**VPS Standard ($12-18/mo)**
```bash
git clone https://github.com/BramAlkema/signal-rag-bot
cd signal-rag-bot
cp .env.example .env && nano .env
docker-compose up -d
```

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

## How It Works

1. **PDF Processing**: Drop PDFs in `input/pdfs/`
2. **Extraction**: Preserves structure (TOC, links, tables)
3. **Metadata**: Extracts titles, authors from PDFs
4. **Bucketing**: Auto-categorizes into semantic buckets (max 2M tokens each)
5. **Upload**: Creates OpenAI Assistant with file search
6. **Bot**: Signal interface for Q&A

## Documentation

- 📖 [Main README](README.md) - Project overview and quick start
- 🐳 [Docker Deployment](DOCKER_DEPLOYMENT.md) - Standard VPS deployment
- 📦 [Small Box Deployment](README_SMALL_BOXES.md) - Budget VPS (1GB RAM)
- ☁️ [Replit Deployment](README_REPLIT.md) - Free cloud hosting
- 📊 [Deployment Options](DEPLOYMENT_OPTIONS.md) - Complete comparison
- 🔄 [Deployment Comparison](DEPLOYMENT_COMPARISON.md) - Migration guide
- 🔒 [Security](security.py) - Production security controls
- 🧪 [Testing](tests/) - 102 tests with >80% coverage

## License

MIT - see [LICENSE](LICENSE) file for details
