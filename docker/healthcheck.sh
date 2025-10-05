#!/bin/bash
# Health check script for Signal RAG Bot container
# Verifies critical components are operational

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[HEALTH]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[HEALTH]${NC} $1"
}

log_error() {
    echo -e "${RED}[HEALTH]${NC} $1"
}

# Track health status
HEALTH_OK=0

# 1. Check Python process is running
log_info "Checking Python process..."
if pgrep -f "python.*signal_bot" > /dev/null; then
    log_info "✓ Python process running"
else
    log_error "✗ Python process not found"
    HEALTH_OK=1
fi

# 2. Check signal-cli is installed and accessible
log_info "Checking signal-cli..."
if command -v signal-cli &> /dev/null; then
    if signal-cli --version &> /dev/null; then
        log_info "✓ signal-cli accessible"
    else
        log_warn "⚠ signal-cli installed but not responsive"
        HEALTH_OK=1
    fi
else
    log_error "✗ signal-cli not found"
    HEALTH_OK=1
fi

# 3. Check FAISS index exists
log_info "Checking FAISS index..."
if [ -f "/app/rag_faiss.index" ]; then
    log_info "✓ FAISS index found"
else
    log_warn "⚠ FAISS index not found at /app/rag_faiss.index"
    # Not critical - might be mounted in different location
fi

# 4. Check metadata file exists
log_info "Checking RAG metadata..."
if [ -f "/app/rag_index.pkl" ]; then
    log_info "✓ RAG metadata found"
else
    log_warn "⚠ RAG metadata not found"
fi

# 5. Check required environment variables
log_info "Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    log_error "✗ OPENAI_API_KEY not set"
    HEALTH_OK=1
else
    log_info "✓ OPENAI_API_KEY is set"
fi

if [ -z "$SIGNAL_PHONE_NUMBER" ]; then
    log_error "✗ SIGNAL_PHONE_NUMBER not set"
    HEALTH_OK=1
else
    log_info "✓ SIGNAL_PHONE_NUMBER is set"
fi

# 6. Check disk space
log_info "Checking disk space..."
DISK_USAGE=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log_warn "⚠ Disk usage high: ${DISK_USAGE}%"
else
    log_info "✓ Disk usage OK: ${DISK_USAGE}%"
fi

# 7. Check if logs directory is writable
log_info "Checking log directory..."
if [ -w "/app/logs" ]; then
    log_info "✓ Logs directory writable"
else
    log_warn "⚠ Logs directory not writable"
fi

# 8. Try to connect to OpenAI API (optional, might be slow)
# Commenting out to avoid slow health checks
# log_info "Checking OpenAI API connectivity..."
# if python3 -c "from openai import OpenAI; import os; OpenAI(api_key=os.getenv('OPENAI_API_KEY')).models.list()" 2>/dev/null; then
#     log_info "✓ OpenAI API accessible"
# else
#     log_warn "⚠ OpenAI API not accessible"
# fi

# Final status
if [ $HEALTH_OK -eq 0 ]; then
    log_info "==================================="
    log_info "✅ Health check PASSED"
    log_info "==================================="
    exit 0
else
    log_error "==================================="
    log_error "❌ Health check FAILED"
    log_error "==================================="
    exit 1
fi
