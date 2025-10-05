# Quick Start Guide

Get your Signal RAG Bot running in 15 minutes.

---

## Prerequisites

Before you begin, ensure you have:

- [x] Signal account (mobile app installed)
- [x] OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- [x] Linux or macOS system
- [x] Docker and Docker Compose installed

!!! tip "Docker Installation"
    Don't have Docker? Install it from [docker.com/get-started](https://www.docker.com/get-started)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/BramAlkema/signal-rag-bot.git
cd signal-rag-bot
```

---

## Step 2: Configure Environment Variables

Create a `.env` file with your credentials:

```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-openai-api-key-here
SIGNAL_PHONE_NUMBER=+31612345678
ACTIVATION_PASSPHRASE=Activate Oracle
LOG_LEVEL=INFO
EOF
```

!!! warning "E.164 Format Required"
    Phone number must be in E.164 format: `+[country_code][number]`

    Examples: `+31612345678` (Netherlands), `+14155552671` (USA)

!!! danger "Keep Your Secrets Safe"
    Never commit `.env` files to git. They are already in `.gitignore`.

---

## Step 3: Build the Docker Image

```bash
docker-compose build
```

Expected output:
```
[+] Building 45.3s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [build 1/4] RUN apt-get update && apt-get install -y gcc g++ make wget
 => [build 2/4] COPY requirements.txt /tmp/
 => [build 3/4] RUN pip install --no-cache-dir -r /tmp/requirements.txt
 => [runtime 1/3] RUN apt-get update && apt-get install -y openjdk-17-jre
 => exporting to image
 => => naming to docker.io/library/signal-rag-bot:latest
```

---

## Step 4: Link Signal Account

Start the container in interactive mode to link your Signal account:

```bash
docker-compose run --rm signal-rag-bot signal-cli link -n "RAG-Bot"
```

A QR code will appear in your terminal. Scan it with your Signal app:

1. Open Signal on your phone
2. Tap your profile → **Linked Devices**
3. Tap **+** (Link New Device)
4. Scan the QR code

!!! success "Linked Successfully"
    You'll see a confirmation message once linking is complete.

---

## Step 5: Prepare Your Knowledge Base

Build the FAISS index from your PDFs:

```bash
# Place your PDFs in the input directory
mkdir -p input
cp /path/to/your/pdfs/*.pdf input/

# Build the RAG index
docker-compose run --rm signal-rag-bot python custom_rag.py build
```

Expected output:
```
Processing PDFs...
✓ Extracted 250 chunks from 5 PDFs
✓ Generated embeddings (1536 dimensions)
✓ Built FAISS index (250 vectors)
✓ Saved to rag_faiss.index and rag_index.pkl
```

!!! info "First Time Setup"
    Building the index takes ~2-5 minutes depending on PDF size and count.

---

## Step 6: Start the Bot

```bash
docker-compose up -d
```

Check the logs to verify it's running:

```bash
docker-compose logs -f signal-rag-bot
```

You should see:
```
[ENTRYPOINT] ✓ Loaded OPENAI_API_KEY from environment
[ENTRYPOINT] ✓ Loaded SIGNAL_PHONE_NUMBER from environment
[ENTRYPOINT] ✓ Environment validation passed
[INFO] Signal RAG Bot starting...
[INFO] Loaded FAISS index with 250 vectors
[INFO] Waiting for messages...
```

!!! success "Bot is Running!"
    Your bot is now live and listening for messages.

---

## Step 7: Test the Bot

Send a message to yourself in Signal:

1. Open Signal app
2. Tap **Note to Self** (or send to your own number)
3. Send: `Activate Oracle`
4. Wait for activation confirmation
5. Ask a question: `What is the main topic of the documents?`

Expected conversation:
```
You: Activate Oracle
Bot: ✅ Activated! You can now ask me questions.

You: What is the main topic of the documents?
Bot: Based on the provided context, the main topic covers...
[Source: document.pdf, page 5]
```

---

## Next Steps

!!! tip "Configuration"
    Learn about all configuration options in the [Configuration Guide](configuration.md)

!!! info "Production Deployment"
    Ready for production? See the [Docker Deployment Guide](../deployment/docker.md)

!!! warning "Security"
    Review the [Security Best Practices](../security/best-practices.md) before exposing your bot

---

## Troubleshooting

### Bot doesn't respond

Check the logs for errors:
```bash
docker-compose logs signal-rag-bot | grep ERROR
```

### QR code not appearing

Ensure you're running in interactive mode:
```bash
docker-compose run --rm signal-rag-bot signal-cli link -n "RAG-Bot"
```

### Index build fails

Verify PDFs are valid and readable:
```bash
ls -lh input/*.pdf
```

### Can't find FAISS index

Ensure you ran the build command and check volumes:
```bash
docker volume ls | grep rag-index
```

---

## Getting Help

- 📖 **Documentation**: Browse the full docs for detailed guides
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/BramAlkema/signal-rag-bot/issues)
- 💬 **Discussions**: Join the community on GitHub Discussions

---

**Congratulations!** You now have a fully functional Signal RAG Bot. 🎉
