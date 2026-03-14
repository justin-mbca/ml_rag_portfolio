# Shared base image for all GenAI Financial Assistant services
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Switch to non-root user
USER appuser
