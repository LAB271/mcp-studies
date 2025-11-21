# Graph Database MCP Server - Docker Deployment

## Overview

This directory contains a complete Docker setup for running the Graph Database MCP Server alongside Neo4j, similar to spike 004.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 2GB+ RAM available for Neo4j

### Start Everything with Docker

```bash
cd spikes/006_graphdb

# Build and start both Neo4j and MCP server
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f graphdb-mcp-server
docker-compose logs -f neo4j
```

### Stop Services

```bash
docker-compose down

# Also remove volumes (optional)
docker-compose down -v
```

## Architecture

```
Docker Network (172.31.0.0/16)
├── neo4j:7687 (Bolt Protocol)
│   ├── Port 7474 (Browser UI)
│   ├── Port 7473 (HTTPS)
│   └── Volumes: neo4j-data, neo4j-logs
│
└── graphdb-mcp-server:8000
    ├── Depends on: neo4j (health check)
    ├── Exposes: MCP tools
    └── Connects to Neo4j via internal network
```

## Services

### 1. Neo4j Database
- **Container Name:** neo4j-graphdb
- **Ports:** 7687 (Bolt), 7474 (Browser), 7473 (HTTPS)
- **Auth:** neo4j / neo4jpassword
- **Memory:** 512MB initial, 1024MB max (configurable)
- **Health Check:** Cypher query validation

### 2. MCP Server
- **Container Name:** graphdb-mcp-server
- **Port:** 8000
- **Depends On:** Neo4j (healthy)
- **Build:** Multi-stage build with minimal production image
- **Health Check:** MCP tool listing

## Environment Variables

You can customize the deployment with a `.env` file:

```bash
# Neo4j Configuration
NEO4J_AUTH=neo4j/custom_password
NEO4J_HEAP_INITIAL=512m
NEO4J_HEAP_MAX=2048m
NEO4J_USER=neo4j
NEO4J_PASSWORD=custom_password
NEO4J_DATABASE=neo4j

# Logging
LOG_LEVEL=info
```

## Accessing Services

### Neo4j Browser
```
http://localhost:7474
Login: neo4j / neo4jpassword
```

### MCP Server Health
```bash
# Check if MCP server is responding
docker-compose exec graphdb-mcp-server python -c "import asyncio; from main_server import get_database_stats; print(asyncio.run(get_database_stats()))"
```

## Docker Images

### Base Image
- `python:3.13-slim` - Minimal Python image

### Build Stages
1. **base** - Platform-specific optimizations
2. **builder** - Install all dependencies
3. **production** - Minimal runtime image with non-root user

### Optimizations
- Multi-stage build reduces image size
- Non-root user (mcp:1000) for security
- Platform-specific builds (AMD64, ARM64)
- Health checks for both services

## Rebuilding

If you modify `main_server.py`:

```bash
# Rebuild the MCP server image
docker-compose build vectordb-mcp-server

# Rebuild and restart
docker-compose up -d --build vectordb-mcp-server
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Verify port availability
lsof -i :7687
lsof -i :7474
lsof -i :8000
```

### Neo4j connection issues
```bash
# Restart Neo4j
docker-compose restart neo4j

# Wait for health check to pass
docker-compose ps  # Check STATUS column
```

### MCP Server not responding
```bash
# Check health
docker-compose exec vectordb-mcp-server python -c "from main_server import handle_list_tools; print('OK')"

# View logs
docker-compose logs vectordb-mcp-server
```

## Data Persistence

- **Neo4j data:** Stored in `neo4j-data` volume (persists between restarts)
- **Neo4j logs:** Stored in `neo4j-logs` volume
- **Vectordb files:** Mounted from `./vectordb` directory

To backup:
```bash
docker-compose exec neo4j cypher-shell -u neo4j -p neo4jpassword CALL apoc.export.json.all('export.json')
```

## Connecting from Cline

The MCP server runs in Docker and is accessible via:

1. **Docker Compose** (Recommended for development)
   ```bash
   docker-compose up -d
   ```

2. **Cline Configuration**
   - Use: `docker-compose exec vectordb-mcp-server python /app/server.py`
   - Or configure with absolute path to local `main_server.py`

## Production Considerations

- Increase Neo4j heap for larger datasets
- Use managed Neo4j service (AWS Neptune, Aura)
- Add nginx reverse proxy for MCP server
- Configure volume backups
- Set up monitoring and alerting

## Development Workflow

```bash
# 1. Start Docker
docker-compose up -d

# 2. Test MCP server
cd spikes/006_graphdb
python3 test_mcp_server.py

# 3. Modify main_server.py
nano main_server.py

# 4. Rebuild and restart
docker-compose up -d --build vectordb-mcp-server

# 5. Verify changes
docker-compose logs -f vectordb-mcp-server
```

## Additional Commands

```bash
# View detailed service info
docker-compose ps -a

# Execute commands in container
docker-compose exec vectordb-mcp-server python -c "..."

# View service logs with timestamp
docker-compose logs --timestamps

# Remove everything (containers, volumes, networks)
docker-compose down -v --remove-orphans

# Check network
docker network inspect 006_vectordb_mcp-network-vectordb
```

---

**Quick Reference:**
```bash
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f        # View logs
docker-compose ps             # Status
docker-compose exec vectordb-mcp-server python ...  # Run commands
