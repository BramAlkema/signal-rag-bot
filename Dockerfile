# ===========================================
# Stage 1: Build Stage
# ===========================================
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Download and prepare signal-cli
WORKDIR /tmp
RUN wget -q https://github.com/AsamK/signal-cli/releases/download/v0.13.9/signal-cli-0.13.9-Linux.tar.gz && \
    tar xf signal-cli-0.13.9-Linux.tar.gz && \
    mv signal-cli-0.13.9 /opt/signal-cli && \
    rm signal-cli-0.13.9-Linux.tar.gz

# ===========================================
# Stage 2: Runtime Stage
# ===========================================
FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy signal-cli from builder
COPY --from=builder /opt/signal-cli /opt/signal-cli
RUN ln -sf /opt/signal-cli/bin/signal-cli /usr/local/bin/signal-cli

# Create app directory
WORKDIR /app

# Copy application code
COPY custom_rag.py .
COPY security.py .
COPY error_handling.py .
COPY monitoring.py .
COPY signal_bot_rag.py .

# Copy Docker-specific scripts
COPY docker/healthcheck.sh /usr/local/bin/healthcheck
COPY docker/entrypoint.sh /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/healthcheck /usr/local/bin/entrypoint

# Create necessary directories
RUN mkdir -p /app/logs /app/index

# Create volume mount points
VOLUME ["/root/.local/share/signal-cli", "/app/index", "/app/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["/usr/local/bin/healthcheck"]

# Expose metrics port (optional, for Prometheus)
EXPOSE 9090

# Use entrypoint script for validation
ENTRYPOINT ["/usr/local/bin/entrypoint"]

# Default command
CMD ["python", "-u", "signal_bot_rag.py"]

# Labels for metadata
LABEL maintainer="Signal RAG Bot"
LABEL description="Production-ready Signal RAG chatbot with FAISS vector store"
LABEL version="1.0.0"
