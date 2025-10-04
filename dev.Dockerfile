FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    vim \
    && rm -rf /var/lib/apt/lists/*


# Python tooling
RUN pip install --no-cache-dir uv

# Docker CLI (für docker-compose im Container)
RUN curl -fsSL https://get.docker.com | sh

# Arbeitsverzeichnis
WORKDIR /workspace

# Keep container running
CMD ["sleep", "infinity"]