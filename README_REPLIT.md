# Deploy Signal RAG Bot on Replit

Complete guide for deploying Signal RAG Bot on Replit.com (free tier supported).

---

## Why Replit?

✅ **Free Tier Available** - Test for free
✅ **No Server Management** - Replit handles infrastructure
✅ **Easy Deployment** - One-click setup
✅ **Built-in Editor** - Code in browser
✅ **Always-On Option** - Keep bot running 24/7 (paid)
✅ **Secrets Management** - Secure credential storage

---

## Quick Start (5 Minutes)

### 1. Fork/Import to Replit

**Option A: Import from GitHub**
1. Go to [replit.com](https://replit.com)
2. Click **+ Create Repl**
3. Select **Import from GitHub**
4. Paste: `https://github.com/your-repo/signal-rag-bot`
5. Click **Import from GitHub**

**Option B: Upload ZIP**
1. Download this repository as ZIP
2. Go to [replit.com](https://replit.com)
3. Click **+ Create Repl**
4. Select **Upload ZIP**
5. Upload the downloaded file

### 2. Configure Secrets

In Replit, go to the **Secrets** tab (🔒 icon) and add:

```
Key: OPENAI_API_KEY
Value: sk-your-openai-api-key-here
```

```
Key: SIGNAL_PHONE_NUMBER
Value: +31612345678
```

```
Key: ACTIVATION_PASSPHRASE
Value: Activate Oracle
```

**Optional secrets:**
```
Key: AUTHORIZED_USERS
Value: +31612345678,+31687654321

Key: LOG_LEVEL
Value: WARNING
```

### 3. Run Setup

In the Replit Shell, run:

```bash
bash setup_replit.sh
```

This will:
- Install Python dependencies
- Download signal-cli
- Create necessary directories
- Verify configuration

### 4. Link Signal Device

In the Replit Shell:

```bash
signal-cli link -n "RAG-Bot"
```

Scan the QR code with Signal app:
1. Open Signal on your phone
2. Tap Settings → Linked Devices
3. Tap + (Link New Device)
4. Scan the QR code

### 5. Build RAG Index (Optional)

**Option A: Upload PDFs to Replit**
1. Create `input` folder in Replit
2. Upload your PDF files
3. Run:
```bash
python custom_rag.py build
```

**Option B: Use Pre-built Index**
1. Build index locally
2. Upload `rag_faiss.index` and `rag_index.pkl` to Replit
3. Place in project root

### 6. Start the Bot

Click the **Run** button at the top of Replit!

Or run manually:
```bash
python signal_bot_rag.py
```

---

## Replit-Specific Optimizations

### Resource Limits

Replit free tier has limited resources:
- **Memory**: ~500MB available
- **CPU**: Shared, lower priority
- **Storage**: 500MB-1GB
- **Always-On**: Not available (bot sleeps when inactive)

### Optimized Configuration

The bot automatically uses lightweight settings on Replit:

```python
# Automatically set when REPL_ID is detected
CHUNK_SIZE = 800       # Smaller chunks
CHUNK_OVERLAP = 150    # Less overlap
SEARCH_K = 2           # Fewer results
MAX_TOKENS = 150       # Shorter responses
LOG_LEVEL = WARNING    # Less logging
```

### Keep Bot Alive (Free Tier)

Replit free tier puts inactive repls to sleep. Options:

**Option 1: UptimeRobot (Recommended)**
1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)
2. Add new monitor:
   - Type: HTTP(s)
   - URL: `https://your-repl-name.your-username.repl.co`
   - Interval: 5 minutes
3. Bot will stay awake as long as it receives pings

**Option 2: Replit Always-On (Paid)**
1. Upgrade to Replit Hacker plan ($7/month)
2. Enable "Always On" for your repl
3. Bot runs 24/7 without interruption

**Option 3: Manual Wake-Up**
- Just open your repl when you want to use the bot
- It will sleep after ~1 hour of inactivity

---

## File Structure

```
signal-rag-bot/
├── .replit                    # Replit configuration
├── replit.nix                 # Nix packages (Java, Python, etc.)
├── setup_replit.sh            # One-time setup script
├── signal_bot_rag.py          # Main bot application
├── custom_rag.py              # RAG implementation
├── security.py                # Security controls
├── error_handling.py          # Error handling
├── monitoring.py              # Monitoring
├── requirements.txt           # Python dependencies
├── logs/                      # Log files (created automatically)
├── index/                     # RAG index storage
└── input/                     # PDF files for indexing
```

---

## Environment Detection

The bot automatically detects Replit and optimizes:

```python
# In signal_bot_rag.py
import os

def is_replit():
    return os.environ.get('REPL_ID') is not None

if is_replit():
    # Use Replit-optimized settings
    os.environ.setdefault('CHUNK_SIZE', '800')
    os.environ.setdefault('LOG_LEVEL', 'WARNING')
    os.environ.setdefault('SEARCH_K', '2')
```

---

## Troubleshooting

### Bot Stops After Inactivity

**Problem:** Replit puts free tier repls to sleep

**Solutions:**
1. Use UptimeRobot to keep awake (free)
2. Upgrade to Always-On ($7/month)
3. Accept sleep mode for testing

### Out of Memory

**Problem:** Process killed due to memory limit

**Solutions:**
1. Reduce index size (fewer PDFs)
2. Use smaller chunks: Set `CHUNK_SIZE=500`
3. Reduce search results: Set `SEARCH_K=1`
4. Upgrade to Replit Hacker plan (more RAM)

### signal-cli Not Found

**Problem:** `signal-cli: command not found`

**Solutions:**
```bash
# Re-run setup script
bash setup_replit.sh

# Or manually add to PATH
export PATH="/home/runner/.local/share/signal-cli-bin/bin:$PATH"

# Verify
signal-cli --version
```

### Slow Response Times

**Problem:** Queries take 10+ seconds

**Solutions:**
1. This is normal on Replit free tier (shared CPU)
2. Reduce `SEARCH_K` to 1
3. Upgrade to Replit Hacker for better performance

### Storage Full

**Problem:** Can't upload more PDFs

**Solutions:**
1. Replit free tier has ~500MB limit
2. Delete unnecessary files:
```bash
# Remove old logs
rm -rf logs/*.log

# Remove test files
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
```
3. Use smaller PDFs or fewer documents
4. Upgrade to Replit Hacker (more storage)

### Secrets Not Loading

**Problem:** Environment variables not set

**Solutions:**
1. Verify secrets in Secrets tab (🔒 icon)
2. Restart the repl (Stop + Run)
3. Check secret names match exactly:
   - `OPENAI_API_KEY` (not `OPENAI_KEY`)
   - `SIGNAL_PHONE_NUMBER` (not `PHONE_NUMBER`)

---

## Replit vs Other Platforms

| Feature | Replit Free | Replit Hacker | VPS (Lite) |
|---------|-------------|---------------|------------|
| **Cost** | $0 | $7/month | $3-6/month |
| **Always-On** | No* | Yes | Yes |
| **Memory** | ~500MB | 1-2GB | 512MB-1GB |
| **CPU** | Shared | Better | 1 vCPU |
| **Setup** | Easy | Easy | Medium |
| **Performance** | Slow | Medium | Fast |

*Can use UptimeRobot to keep awake

---

## Advanced Configuration

### Custom Domain (Replit Hacker)

1. Enable Always-On
2. Go to repl settings
3. Add custom domain
4. Update UptimeRobot to use custom domain

### Database Integration

Replit provides built-in database:

```python
# Optional: Use Replit DB for conversation history
from replit import db

# Store conversation
db[f"user_{user_id}"] = conversation_history

# Retrieve
history = db.get(f"user_{user_id}", [])
```

### Multiple Repls

Run multiple bots:
1. Fork this repl for each bot
2. Use different Signal accounts
3. Set different `ACTIVATION_PASSPHRASE` for each

---

## Performance Tips

### Optimize for Replit

```bash
# In Secrets tab, add:
CHUNK_SIZE=500          # Very small chunks
SEARCH_K=1              # Only 1 result
MAX_TOKENS=100          # Short responses
LOG_LEVEL=ERROR         # Minimal logging
PYTHONOPTIMIZE=1        # Python optimizations
```

### Reduce Index Size

```bash
# Only index most important PDFs
mkdir input/priority
cp important.pdf input/priority/
python custom_rag.py build --input-dir input/priority
```

### Monitor Resources

```bash
# Check memory usage
ps aux | grep python

# Check disk usage
df -h

# Check log size
du -sh logs/
```

---

## Limitations on Replit

### Free Tier
- ⚠️ Sleeps after 1 hour of inactivity
- ⚠️ Limited to ~500MB RAM
- ⚠️ Shared CPU (slower)
- ⚠️ ~500MB storage
- ⚠️ No custom domain

### Hacker Plan ($7/month)
- ✅ Always-On available
- ✅ More RAM (1-2GB)
- ✅ Better CPU priority
- ✅ More storage (2-5GB)
- ✅ Custom domains

### What Works Well
- ✅ Testing and development
- ✅ Personal use (1-3 users)
- ✅ Low query volume (<50/day)
- ✅ Quick prototyping
- ✅ Learning and demos

### What Doesn't Work Well
- ❌ High traffic (>10 concurrent users)
- ❌ Large indexes (>1000 chunks)
- ❌ 24/7 uptime (free tier)
- ❌ Fast response times (<3s)

---

## Migration Guide

### From Replit to VPS

When you outgrow Replit:

```bash
# 1. Export data from Replit
# Download these files:
# - rag_faiss.index
# - rag_index.pkl
# - Signal data from /home/runner/.local/share/signal-cli

# 2. Set up VPS (see README_SMALL_BOXES.md)
git clone https://github.com/your-repo/signal-rag-bot
cd signal-rag-bot

# 3. Copy data
# Upload the downloaded files to VPS

# 4. Deploy
docker-compose -f docker-compose.lite.yml up -d
```

### From VPS to Replit

To test locally first:

```bash
# 1. Build index locally
python custom_rag.py build

# 2. Upload to Replit
# Upload rag_faiss.index and rag_index.pkl

# 3. Link Signal on Replit
# Run setup and link as described above
```

---

## Security on Replit

### Best Practices

1. **Always use Secrets tab** - Never hardcode credentials
2. **Keep repl private** - Don't make it public
3. **Regularly rotate API keys** - Monthly recommended
4. **Monitor usage** - Check Replit analytics
5. **Use AUTHORIZED_USERS** - Limit who can activate bot

### Accessing Secrets

Secrets are available as environment variables:

```python
import os

# Replit automatically injects secrets
api_key = os.environ.get('OPENAI_API_KEY')
phone = os.environ.get('SIGNAL_PHONE_NUMBER')
```

---

## Cost Comparison

### Monthly Costs

| Tier | Cost | Always-On | Performance | Best For |
|------|------|-----------|-------------|----------|
| **Replit Free** | $0 | No* | Slow | Testing |
| **Replit + UptimeRobot** | $0 | Yes* | Slow | Personal |
| **Replit Hacker** | $7 | Yes | Medium | Small team |
| **VPS Lite** | $3-6 | Yes | Fast | Production |
| **VPS Standard** | $12-18 | Yes | Fastest | High traffic |

*With workarounds

---

## Getting Help

### Replit-Specific Issues

1. Check Replit status: [status.replit.com](https://status.replit.com)
2. Replit community: [ask.replit.com](https://ask.replit.com)
3. Replit docs: [docs.replit.com](https://docs.replit.com)

### Bot-Specific Issues

1. Check logs: `cat logs/bot.log`
2. Test components:
   ```bash
   # Test signal-cli
   signal-cli --version

   # Test Python
   python -c "import openai; print('OK')"

   # Test RAG
   python custom_rag.py test
   ```

---

## Next Steps

1. ✅ Complete setup (Steps 1-6 above)
2. 🧪 Test with a simple query
3. 📚 Add your PDF documents
4. 🚀 Share with authorized users
5. 📊 Monitor usage and performance
6. ⚡ Upgrade to VPS when needed

---

**Ready to deploy?** Follow the Quick Start section above! 🚀

**Questions?** Open an issue on GitHub or ask on Replit community.
