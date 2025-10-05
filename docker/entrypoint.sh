#!/bin/bash
# Entrypoint script for Signal RAG Bot
# Validates environment and starts the application

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[ENTRYPOINT]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[ENTRYPOINT]${NC} $1"
}

log_error() {
    echo -e "${RED}[ENTRYPOINT]${NC} $1"
}

log_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Start validation
log_header "Signal RAG Bot - Environment Validation"

# Track validation errors
VALIDATION_FAILED=0

# ========================================
# 1. Required Environment Variables
# ========================================
log_info "Validating required environment variables..."

# Check OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    log_error "OPENAI_API_KEY is not set"
    VALIDATION_FAILED=1
elif [[ ! "$OPENAI_API_KEY" =~ ^sk-[a-zA-Z0-9_-]+$ ]]; then
    log_error "OPENAI_API_KEY format is invalid (should start with 'sk-')"
    VALIDATION_FAILED=1
else
    log_info "✓ OPENAI_API_KEY is set and valid format"
fi

# Check SIGNAL_PHONE_NUMBER
if [ -z "$SIGNAL_PHONE_NUMBER" ]; then
    log_error "SIGNAL_PHONE_NUMBER is not set"
    VALIDATION_FAILED=1
elif [[ ! "$SIGNAL_PHONE_NUMBER" =~ ^\+[1-9][0-9]{7,14}$ ]]; then
    log_error "SIGNAL_PHONE_NUMBER format is invalid (should be E.164 format: +31612345678)"
    VALIDATION_FAILED=1
else
    log_info "✓ SIGNAL_PHONE_NUMBER is set and valid format"
fi

# ========================================
# 2. Optional Environment Variables
# ========================================
log_info "Checking optional environment variables..."

# ACTIVATION_PASSPHRASE
if [ -z "$ACTIVATION_PASSPHRASE" ]; then
    log_warn "ACTIVATION_PASSPHRASE not set, using default"
    export ACTIVATION_PASSPHRASE="Activate Oracle"
else
    log_info "✓ ACTIVATION_PASSPHRASE is set"
fi

# AUTHORIZED_USERS
if [ -z "$AUTHORIZED_USERS" ]; then
    log_warn "AUTHORIZED_USERS not set, all users will be allowed after activation"
else
    log_info "✓ AUTHORIZED_USERS is set"
fi

# LOG_LEVEL
if [ -z "$LOG_LEVEL" ]; then
    export LOG_LEVEL="INFO"
    log_info "LOG_LEVEL not set, using default: INFO"
else
    log_info "✓ LOG_LEVEL set to: $LOG_LEVEL"
fi

# ========================================
# 3. Docker Secrets Support
# ========================================
log_info "Checking for Docker secrets..."

# Check for OpenAI API key in Docker secret
if [ -f "/run/secrets/openai_api_key" ]; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai_api_key)
    log_info "✓ Loaded OPENAI_API_KEY from Docker secret"
fi

# Check for Signal phone number in Docker secret
if [ -f "/run/secrets/signal_phone_number" ]; then
    export SIGNAL_PHONE_NUMBER=$(cat /run/secrets/signal_phone_number)
    log_info "✓ Loaded SIGNAL_PHONE_NUMBER from Docker secret"
fi

# Check for activation passphrase in Docker secret
if [ -f "/run/secrets/activation_passphrase" ]; then
    export ACTIVATION_PASSPHRASE=$(cat /run/secrets/activation_passphrase)
    log_info "✓ Loaded ACTIVATION_PASSPHRASE from Docker secret"
fi

# ========================================
# 4. File System Checks
# ========================================
log_info "Checking file system..."

# Check signal-cli directory
if [ ! -d "/root/.local/share/signal-cli" ]; then
    log_warn "Signal-cli data directory not found, creating..."
    mkdir -p /root/.local/share/signal-cli
fi

# Check logs directory
if [ ! -d "/app/logs" ]; then
    log_warn "Logs directory not found, creating..."
    mkdir -p /app/logs
fi

# Check index directory
if [ ! -d "/app/index" ]; then
    log_warn "Index directory not found, creating..."
    mkdir -p /app/index
fi

# ========================================
# 5. Dependency Checks
# ========================================
log_info "Checking dependencies..."

# Check signal-cli
if ! command -v signal-cli &> /dev/null; then
    log_error "signal-cli not found in PATH"
    VALIDATION_FAILED=1
else
    SIGNAL_CLI_VERSION=$(signal-cli --version 2>&1 | head -1)
    log_info "✓ signal-cli found: $SIGNAL_CLI_VERSION"
fi

# Check Python dependencies
if python -c "import openai" 2>/dev/null; then
    log_info "✓ OpenAI Python package installed"
else
    log_error "OpenAI Python package not installed"
    VALIDATION_FAILED=1
fi

if python -c "import faiss" 2>/dev/null; then
    log_info "✓ FAISS Python package installed"
else
    log_error "FAISS Python package not installed"
    VALIDATION_FAILED=1
fi

# ========================================
# 6. RAG Index Check
# ========================================
log_info "Checking RAG index files..."

if [ -f "/app/rag_faiss.index" ]; then
    log_info "✓ FAISS index found at /app/rag_faiss.index"
elif [ -f "/app/index/rag_faiss.index" ]; then
    log_info "✓ FAISS index found at /app/index/rag_faiss.index"
    # Create symlink for convenience
    ln -sf /app/index/rag_faiss.index /app/rag_faiss.index
    ln -sf /app/index/rag_index.pkl /app/rag_index.pkl
else
    log_warn "⚠ FAISS index not found - bot may fail to start"
    log_warn "  Ensure index files are mounted to /app/index/ or /app/"
fi

# ========================================
# 7. Final Validation
# ========================================
if [ $VALIDATION_FAILED -eq 1 ]; then
    log_header "❌ Validation FAILED - Cannot start"
    log_error "Please fix the above errors and restart the container"
    exit 1
fi

log_header "✅ Validation PASSED - Starting bot"

# ========================================
# 8. Start Application
# ========================================
log_info "Starting Signal RAG Bot..."
log_info "Command: $@"

# Execute the main command
exec "$@"
