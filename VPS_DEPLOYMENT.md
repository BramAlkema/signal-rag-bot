# Deploy Signal RAG Bot to Your VPS

## Prerequisites

- VPS with Ubuntu/Debian (any cheap $5-10/month VPS works)
- SSH access to your VPS
- Your VPS IP address

## Step 1: Prepare Your VPS

SSH into your VPS:
```bash
ssh user@your-vps-ip
```

Update system and install dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv openjdk-17-jre-headless wget curl git
```

## Step 2: Install signal-cli

```bash
# Download signal-cli
cd /opt
sudo wget https://github.com/AsamK/signal-cli/releases/download/v0.13.9/signal-cli-0.13.9-Linux.tar.gz
sudo tar xf signal-cli-0.13.9-Linux.tar.gz
sudo ln -sf /opt/signal-cli-0.13.9/bin/signal-cli /usr/local/bin/

# Verify installation
signal-cli --version
```

## Step 3: Upload Your Bot Code

From your local machine:
```bash
# Navigate to RAG project
cd /Users/ynse/projects/RAG

# Copy files to VPS
scp signal_bot_linked.py user@your-vps-ip:~/
scp -r output/ user@your-vps-ip:~/
```

Or use git:
```bash
# On VPS
cd ~
git clone YOUR_REPO_URL rag-bot
cd rag-bot
```

## Step 4: Set Up Python Environment

On VPS:
```bash
cd ~/
python3 -m venv venv
source venv/bin/activate
pip install openai requests
```

## Step 5: Set Environment Variables

```bash
# Create .env file
cat > ~/.env << 'EOF'
export OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"
EOF

# Load it
source ~/.env
```

Or add to ~/.bashrc for persistence:
```bash
echo 'export OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
```

## Step 6: Link Signal Account

**IMPORTANT: Do this step from your VPS terminal!**

```bash
# Generate QR code for linking
signal-cli link -n "RAG-Bot"
```

This will show a QR code in the terminal. On your phone:
1. Open Signal
2. Settings → Linked Devices
3. Link New Device
4. Scan the QR code

## Step 7: Test the Bot

```bash
source venv/bin/activate
python3 signal_bot_linked.py
```

Send a test message to yourself on Signal. The bot should respond!

Press `Ctrl+C` to stop the test.

## Step 8: Run as Background Service (systemd)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/signal-rag-bot.service
```

Paste this (replace `USER` with your username):

```ini
[Unit]
Description=Signal RAG Chatbot
After=network.target

[Service]
Type=simple
User=USER
WorkingDirectory=/home/USER
Environment="OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE"
ExecStart=/home/USER/venv/bin/python3 /home/USER/signal_bot_linked.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable signal-rag-bot

# Start the service
sudo systemctl start signal-rag-bot

# Check status
sudo systemctl status signal-rag-bot

# View logs
sudo journalctl -u signal-rag-bot -f
```

## Managing the Bot

### Check if running
```bash
sudo systemctl status signal-rag-bot
```

### View logs
```bash
sudo journalctl -u signal-rag-bot -f
```

### Restart bot
```bash
sudo systemctl restart signal-rag-bot
```

### Stop bot
```bash
sudo systemctl stop signal-rag-bot
```

### Update bot code
```bash
# Stop the service
sudo systemctl stop signal-rag-bot

# Update files (via scp or git pull)
cd ~/
# ... update files ...

# Restart
sudo systemctl start signal-rag-bot
```

## Step 9: Set Up Authorized Users (Optional)

Edit `signal_bot_linked.py`:

```python
# Around line 20
AUTHORIZED_USERS = [
    "+1234567890",  # Your number
    "+0987654321",  # Friend's number
]
```

Then restart:
```bash
sudo systemctl restart signal-rag-bot
```

## Firewall Setup (Optional but Recommended)

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Signal uses outbound connections only (no ports needed)
```

## Monitoring

### Check disk space
```bash
df -h
```

### Check memory usage
```bash
free -h
```

### Monitor bot process
```bash
htop
# Look for python3 signal_bot_linked.py
```

## Troubleshooting

### Bot not responding
```bash
# Check logs
sudo journalctl -u signal-rag-bot -n 100

# Check if process is running
ps aux | grep signal_bot

# Test signal-cli manually
signal-cli receive
```

### "No linked account" error
You need to re-link on the VPS:
```bash
signal-cli link -n "RAG-Bot"
# Scan QR again
```

### OpenAI quota errors
Add credits at: https://platform.openai.com/account/billing

### Memory issues
If VPS has <1GB RAM, the bot might crash. Consider:
- Upgrading VPS to 1GB+ RAM
- Adding swap space:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Cost Estimate

- **VPS**: $5-10/month (DigitalOcean, Linode, Hetzner)
- **OpenAI API**: ~$1-5/month (depending on usage)
- **Signal**: Free

**Total: ~$6-15/month**

## Security Best Practices

1. **Keep system updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Use SSH keys** (disable password auth):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

3. **Restrict authorized users** in the bot code

4. **Monitor logs** for unusual activity

5. **Backup signal-cli data** periodically:
   ```bash
   tar -czf signal-backup.tar.gz ~/.local/share/signal-cli
   ```

## Next Steps

1. ✅ Deploy bot to VPS
2. ✅ Link Signal account
3. ✅ Set up systemd service
4. ✅ Test with yourself
5. ✅ Add authorized users
6. 🚀 Share with friends/team!

---

Your Signal RAG bot is now running 24/7 on your VPS! 🎉
