#!/bin/bash
# Setup script for Replit deployment
# Run this once when first deploying to Replit

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Signal RAG Bot - Replit Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if running on Replit
if [ -z "$REPL_ID" ]; then
    echo "⚠️  Warning: Not running on Replit"
    echo "This script is optimized for Replit environment"
fi

# Install Python dependencies
echo ""
echo "[1/5] Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Download signal-cli
echo ""
echo "[2/5] Downloading signal-cli..."
SIGNAL_CLI_VERSION="0.13.9"
SIGNAL_CLI_DIR="/home/runner/.local/share/signal-cli-bin"

if [ ! -d "$SIGNAL_CLI_DIR" ]; then
    mkdir -p "$SIGNAL_CLI_DIR"
    cd /tmp
    wget -q "https://github.com/AsamK/signal-cli/releases/download/v${SIGNAL_CLI_VERSION}/signal-cli-${SIGNAL_CLI_VERSION}-Linux.tar.gz"
    tar xf "signal-cli-${SIGNAL_CLI_VERSION}-Linux.tar.gz"
    mv "signal-cli-${SIGNAL_CLI_VERSION}"/* "$SIGNAL_CLI_DIR/"
    rm -rf "signal-cli-${SIGNAL_CLI_VERSION}" "signal-cli-${SIGNAL_CLI_VERSION}-Linux.tar.gz"
    cd -
fi

# Add signal-cli to PATH
echo ""
echo "[3/5] Configuring signal-cli..."
if [ ! -L "/usr/local/bin/signal-cli" ]; then
    ln -sf "$SIGNAL_CLI_DIR/bin/signal-cli" /usr/local/bin/signal-cli 2>/dev/null || \
    export PATH="$SIGNAL_CLI_DIR/bin:$PATH"
fi

# Create necessary directories
echo ""
echo "[4/5] Creating directories..."
mkdir -p logs
mkdir -p index
mkdir -p /home/runner/.local/share/signal-cli

# Verify environment variables
echo ""
echo "[5/5] Verifying configuration..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set!"
    echo "   → Go to Secrets tab and add OPENAI_API_KEY"
    exit 1
else
    echo "✅ OPENAI_API_KEY is set"
fi

if [ -z "$SIGNAL_PHONE_NUMBER" ]; then
    echo "❌ SIGNAL_PHONE_NUMBER not set!"
    echo "   → Go to Secrets tab and add SIGNAL_PHONE_NUMBER"
    exit 1
else
    echo "✅ SIGNAL_PHONE_NUMBER is set"
fi

# Set optimal environment variables for Replit
export LOG_LEVEL="${LOG_LEVEL:-WARNING}"
export CHUNK_SIZE="${CHUNK_SIZE:-800}"
export CHUNK_OVERLAP="${CHUNK_OVERLAP:-150}"
export SEARCH_K="${SEARCH_K:-2}"
export MAX_TOKENS="${MAX_TOKENS:-150}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Link Signal device:"
echo "   → Run: signal-cli link -n \"RAG-Bot\""
echo "   → Scan QR code with Signal app"
echo ""
echo "2. Build RAG index (optional):"
echo "   → Place PDFs in input/ directory"
echo "   → Run: python custom_rag.py build"
echo ""
echo "3. Start the bot:"
echo "   → Click 'Run' button"
echo "   → Or run: python signal_bot_rag.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
