#!/bin/bash
# Wrapper script to start Docker containers and MCP server
# This ensures Neo4j and MCP server are running before Cline connects

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Starting Docker containers for graph database..." >&2

# Start Docker containers in background if not running
if ! docker-compose ps | grep -q "graphdb-mcp-server.*Up"; then
  echo "Starting docker-compose services..." >&2
  docker-compose up -d
  
  # Wait for services to be healthy
  echo "Waiting for services to be healthy..." >&2
  sleep 10
fi

# Run the MCP server
echo "Starting MCP server..." >&2
docker-compose exec -T vectordb-mcp-server python /app/server.py
