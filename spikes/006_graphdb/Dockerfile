# Dockerfile for Vector Database MCP Server
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

# Accept platform arguments from buildx
ARG TARGETPLATFORM
ARG BUILDPLATFORM

FROM python:3.13-slim AS base

# Platform-specific optimizations
RUN case "${TARGETPLATFORM}" in \
    "linux/amd64") \
        echo "Building for AMD64 (AWS Fargate compatible)" \
        ;; \
    "linux/arm64") \
        echo "Building for ARM64 (M1/M2 Mac and AWS Graviton compatible)" \
        ;; \
    *) \
        echo "Building for platform: ${TARGETPLATFORM}" \
        ;; \
    esac

# ===================================
# Builder Stage
# ===================================
FROM base AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir --user \
    aiohttp==3.13.2 \
    mcp[cli]==1.20.0 \
    neo4j==6.0.3 \
    pdfplumber==0.11.8 \
    sentence-transformers==5.1.2

# ===================================
# Production Stage
# ===================================
FROM base AS production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app

COPY --from=builder /root/.local /home/mcp/.local

ARG BUILD_CONTEXT=spikes/006_graphdb
ARG PACKAGE_CONTEXT=.

# Set working directory
WORKDIR /app

COPY ${BUILD_CONTEXT}/main_server.py server.py

RUN chown mcp:mcp /app/server.py && chmod 755 /app/server.py

USER mcp

# Health check - verify MCP server port is open
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); result = s.connect_ex(('localhost', 8000)); exit(result)" || exit 1

ENV PATH=/home/mcp/.local/bin:$PATH
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port (for reference, MCP uses stdio by default)
EXPOSE 8000

# Run the MCP server
CMD ["python", "server.py"]
