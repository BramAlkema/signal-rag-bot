# Dockerfile for Signal RAG Bot
FROM python:3.11-slim

# Install Java (required for signal-cli)
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install signal-cli
RUN wget https://github.com/AsamK/signal-cli/releases/download/v0.13.9/signal-cli-0.13.9-Linux.tar.gz \
    && tar xf signal-cli-0.13.9-Linux.tar.gz -C /opt \
    && ln -sf /opt/signal-cli-0.13.9/bin/signal-cli /usr/local/bin/ \
    && rm signal-cli-0.13.9-Linux.tar.gz

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY signal_bot_linked.py .

# Signal-cli data will be mounted as volume
VOLUME /root/.local/share/signal-cli

# Run the bot
CMD ["python", "-u", "signal_bot_linked.py"]
