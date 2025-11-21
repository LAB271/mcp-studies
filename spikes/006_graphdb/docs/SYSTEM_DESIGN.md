# System Design: Neo4j with Vector Database Support

## Overview

Clean setup for Neo4j Graph Database with native MCP support and vector database integration.

Components:
1. **Neo4j Graph Database**: Graph data store with native MCP interface
2. **Vector Database Storage**: Local folder structure for embeddings and documents

## Architecture Components

### Neo4j Graph Database
- **Version**: 5.x (latest stable)
- **Port**: 7687 (Bolt protocol), 7474 (HTTP browser)
- **Role**: Graph data store for relationships and entities
- **Use Cases**:
  - Package relationships (sender, receiver, delivery paths)
  - Delivery driver relationships and routes
  - Geographic/location graphs
  - Complex queries requiring traversal

**Volumes**:
- `neo4j-data`: Persistent graph database storage
- `neo4j-logs`: Database logs

**Credentials**: Configured via environment variables
- Default user: `neo4j`
- Password: Set via `NEO4J_AUTH` environment variable

### 4. Vector Database (Separate Container or Service)
- **Purpose**: Store and search vector embeddings
- **Use Cases**:
  - Semantic search over package descriptions
  - Delivery route optimization via embeddings
  - Document/content similarity search

**Data Location**: `/app/graph_data/` directory for files
- `documents/`: Source files for vectorization
- `embeddings/`: Processed embeddings
- `metadata/`: Associated metadata files
- **Version**: 5.x (latest stable)
- **Ports**:
  - 7687: Bolt protocol (native driver connections)
  - 7474: HTTP (Neo4j Browser and REST API)
  - 7473: HTTPS (secure connections)
- **MCP Support**: Native MCP interface for tool integration
- **Role**: Graph data store with native query capabilities

**Volumes**:
- `neo4j-data`: Persistent graph database storage
- `neo4j-logs`: Database logs
- `graph_data`: Mounted for vector embeddings access

**Credentials**:
- Default user: `neo4j`
- Password: `${NEO4J_AUTH}` environment variable
- **Version**: 5.x (latest stable)
- **Port**: 7687 (Bolt protocol), 7474 (HTTP browser)
- **Role**: Graph data store for relationships and entities
- **Use Cases**:
  - Package relationships (sender, receiver, delivery paths)
  - Delivery driver relationships and routes
  - Geographic/location graphs
  - Complex queries requiring traversal

**Volumes**:
- `neo4j-data`: Persistent graph database storage
- `neo4j-logs`: Database logs

**Credentials**: Configured via environment variables
- Default user: `neo4j`
- Password: Set via `NEO4J_AUTH` environment variable

### 4. Vector Database (Separate Container or Service)
- **Purpose**: Store and search vector embeddings
- **Use Cases**:
  - Semantic search over package descriptions
  - Delivery route optimization via embeddings
  - Document/content similarity search

**Data Location**: `/app/graph_data/` directory for files
- `documents/`: Source files for vectorization
- `embeddings/`: Processed embeddings
- `metadata/`: Associated metadata files

## Directory Structure

```
spikes/006_graphdb/
├── SYSTEM_DESIGN.md           # This file
├── docker-compose.yml         # Neo4j Docker configuration
├── .env                       # Environment variables
├── .ssl-certs/                # SSL certificates (optional)
└── graph_data/                # Vector database files
    ├── documents/             # Source files for vectorization
    │   └── README.md
    └── embeddings/            # Processed embeddings storage
```

## Service Architecture

```
Neo4j Graph Database (Port 7687, 7474, 7473)
├── Native MCP Interface
├── Graph Data Storage
└── Vector Database Access (/app/vectordb)
```

## Data Flow

### Graph Operations
```
Neo4j MCP Interface → Cypher Queries → Graph Database → Results
```

### Vector Operations
```
Raw Documents (vectordb/documents/) → Processing → Embeddings (vectordb/embeddings/)
```

## Network Configuration

**Network Name**: `mcp-network-vectordb`
**Subnet**: `172.31.0.0/16` (Docker bridge)

**Neo4j Access**:
- Bolt Protocol: `bolt://localhost:7687`
- Browser: `http://localhost:7474`
- HTTPS: `https://localhost:7473`

| Volume | Type | Mount Path | Purpose |
|--------|------|-----------|---------|
| `neo4j-data` | Named | `/var/lib/neo4j/data` | Graph database storage |
| `neo4j-logs` | Named | `/var/lib/neo4j/logs` | Database logs |
| `vectordb` | Bind | `/app/vectordb` | Vector embeddings & docs |

## Environment Variables

```bash
# Logging
LOG_LEVEL=info
PYTHONUNBUFFERED=1

# Neo4j Configuration
NEO4J_AUTH=neo4j/neo4jpassword
NEO4J_server_memory_heap_initial__size=512m
NEO4J_server_memory_heap_max__size=1024m
```

## Build and Deployment

### Docker Compose
```bash
cd spikes/006_vectorDb

# Start Neo4j
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f neo4j

# Stop services
docker-compose down
```

### Production Considerations
- Use managed Neo4j instances (Neo4j Aura)
- Configure authentication securely
- Set appropriate memory limits
- Enable backups and replication
- Monitor database performance

## Security

- Neo4j authentication (username/password)
- Network isolation via Docker bridge
- Environment variable configuration
- Data persistence in named volumes

## Monitoring and Logging

**Log Locations**:
- Neo4j: Docker named volume `neo4j-logs`
- Browser: http://localhost:7474

**Health Checks**:
- Cypher Shell connectivity check
- Database availability verification

## Future Enhancements

1. **Dedicated Vector Database**: Pinecone, Weaviate, or Qdrant integration
2. **Backup Strategy**: Automated Neo4j backups
3. **Performance Tuning**: Query optimization and indexing
4. **Monitoring**: Prometheus metrics and Grafana dashboards
5. **Clustering**: Multi-instance Neo4j cluster setup
6. **Semantic Search**: LLM-powered embedding generation

## References

- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [Neo4j Docker Documentation](https://neo4j.com/docs/docker/current/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [NGINX Configuration](https://nginx.org/en/docs/)
