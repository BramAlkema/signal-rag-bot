# Deploy Signal RAG Bot with Docker

## Quick Start (5 minutes)

### 1. Copy Files to Your Server

```bash
# From your local machine
cd /Users/ynse/projects/RAG

# Upload to server
scp -r Dockerfile docker-compose.yml requirements.txt signal_bot_linked.py .env.example user@your-server:/home/user/signal-bot/
```

### 2. On Your Server

```bash
# SSH into server
ssh user@your-server

# Navigate to directory
cd ~/signal-bot

# Create .env file
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the bot (for linking)
docker-compose run --rm signal-rag-bot signal-cli link -n "RAG-Bot"
```

This will show a QR code. **Scan it with Signal on your phone:**
- Settings → Linked Devices → Link New Device

### 4. Start the Bot

```bash
# Start in background
docker-compose up -d

# Check logs
docker-compose logs -f
```

✅ Done! Your bot is running 24/7.

---

## Managing the Bot

### View Logs
```bash
docker-compose logs -f signal-rag-bot
```

### Stop Bot
```bash
docker-compose down
```

### Restart Bot
```bash
docker-compose restart
```

### Update Bot Code
```bash
# Upload new signal_bot_linked.py
scp signal_bot_linked.py user@your-server:/home/user/signal-bot/

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
docker-compose exec signal-rag-bot bash
```

---

## Project Structure

```
signal-bot/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Orchestration config
├── requirements.txt        # Python dependencies
├── signal_bot_linked.py    # Bot code
├── .env                    # Environment variables (your API key)
├── signal-data/            # Persisted Signal account (created automatically)
└── logs/                   # Log files (optional)
```

---

## Troubleshooting

### "QR code not showing"
```bash
# Run interactively
docker-compose run --rm signal-rag-bot signal-cli link -n "RAG-Bot"
```

### "Bot not responding"
```bash
# Check logs
docker-compose logs -f

# Check if running
docker-compose ps

# Restart
docker-compose restart
```

### "Container keeps restarting"
```bash
# View error logs
docker-compose logs --tail=50

# Common issues:
# - OPENAI_API_KEY not set in .env
# - Signal account not linked
```

### "Need to re-link Signal"
```bash
# Stop the bot
docker-compose down

# Remove signal data
rm -rf signal-data/

# Re-link
docker-compose run --rm signal-rag-bot signal-cli link -n "RAG-Bot"

# Start again
docker-compose up -d
```

### "Out of memory"
```bash
# Check container memory
docker stats signal-rag-bot

# Add memory limit in docker-compose.yml:
# mem_limit: 512m
```

---

## Advanced Configuration

### Auto-restart on Boot

Add to docker-compose.yml:
```yaml
restart: always  # Already included
```

### Set Up Log Rotation

Already configured with:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Run Multiple Bots

Create multiple directories:
```bash
# Bot 1 (on port 8001)
cd ~/signal-bot-1
# Edit docker-compose.yml, change container name

# Bot 2 (on port 8002)
cd ~/signal-bot-2
# Edit docker-compose.yml, change container name
```

### Backup Signal Data

```bash
# Create backup
tar -czf signal-backup-$(date +%Y%m%d).tar.gz signal-data/

# Restore backup
tar -xzf signal-backup-20250105.tar.gz
```

---

## Monitoring

### Check Docker Stats
```bash
docker stats signal-rag-bot
```

### View Live Logs
```bash
docker-compose logs -f --tail=100
```

### Disk Usage
```bash
docker system df
```

### Clean Up Old Images
```bash
docker system prune -a
```

---

## Security

### Limit Container Resources
Edit `docker-compose.yml`:
```yaml
services:
  signal-rag-bot:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Use Docker Secrets (Production)
Instead of `.env`:
```bash
# Create secret
echo "your-api-key" | docker secret create openai_key -

# Use in docker-compose.yml:
secrets:
  - openai_key
```

---

## Cost

- **Server**: Already have it ✅
- **Docker**: Free
- **OpenAI API**: ~$1-5/month
- **Signal**: Free

**Total: ~$1-5/month** (just API costs)

---

## One-Line Deploy

If you want to automate everything:

```bash
# On your server, create deploy.sh:
#!/bin/bash
cd ~/signal-bot
git pull  # if using git
docker-compose down
docker-compose build
docker-compose up -d
docker-compose logs -f --tail=50
```

Then just run:
```bash
./deploy.sh
```

---

## Next Steps

1. ✅ Copy files to server
2. ✅ Set OPENAI_API_KEY in .env
3. ✅ Build with docker-compose build
4. ✅ Link Signal account
5. ✅ Start with docker-compose up -d
6. 🎉 Message yourself to test!

Your Signal RAG bot is now Dockerized and running 24/7! 🐳
