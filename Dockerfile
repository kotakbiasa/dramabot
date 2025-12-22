# DramaBot - Telegram Drama Streaming Bot
FROM python:3.13-slim

# Metadata
LABEL maintainer="DramaBot"
LABEL description="Telegram bot untuk streaming drama ke voice chat"
LABEL version="1.0.0"

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir -U pip \
    && pip3 install --no-cache-dir -U -r requirements.txt

# Copy application code
COPY . .

# Run bot
CMD ["bash", "start"]
