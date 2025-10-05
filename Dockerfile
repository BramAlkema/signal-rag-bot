# Dockerfile for Signal RAG Bot
FROM python:3.11-slim

# Install Java (required for signal-cli) and git
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install signal-cli
RUN wget https://github.com/AsamK/signal-cli/releases/download/v0.13.9/signal-cli-0.13.9-Linux.tar.gz \
    && tar xf signal-cli-0.13.9-Linux.tar.gz -C /opt \
    && ln -sf /opt/signal-cli-0.13.9/bin/signal-cli /usr/local/bin/ \
    && rm signal-cli-0.13.9-Linux.tar.gz

# Set working directory
WORKDIR /app

# Clone repository
ARG REPO_URL=https://github.com/BramAlkema/signal-rag-bot.git
RUN git clone ${REPO_URL} . && rm -rf .git

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Signal-cli data will be mounted as volume
VOLUME /root/.local/share/signal-cli

# Run the bot
CMD ["python", "-u", "signal_bot_linked.py"]
