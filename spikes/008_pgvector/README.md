# Spike 008: PostgreSQL + pgvector (Hybrid RAG)

This spike demonstrates a hybrid data system using PostgreSQL with the `pgvector` extension. It combines structured time-series sensor data with unstructured knowledge (manuals, notes) searchable via vector embeddings.

## 🎯 Goals

- **Hybrid Storage**: Store structured (SQL) and unstructured (Vector) data in the same DB.
- **RAG Capability**: Retrieve knowledge based on semantic meaning, not just keywords.
- **Time-Series**: Handle sensor readings efficiently.
- **MCP Integration**: Expose these capabilities as tools to an LLM.

## 🏗 Architecture

- **Database**: PostgreSQL 16 with `pgvector` extension.
- **Server**: Python FastMCP server.
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (runs locally).
- **Infrastructure**: Docker Compose.

## 📂 Structure

- `main_server.py`: The MCP server implementation.
- `generate_data.py`: Script to seed the database with mock sensors, readings, and knowledge.
- `init.sql`: Database schema (Sensors, Readings, Knowledge).
- `docker-compose.yml`: Orchestration.

## 🚀 Usage

### 1. Start the Environment

```bash
make up
```

This starts Postgres and the MCP server.

### 2. Seed Data

Populate the database with mock sensors, readings, and knowledge:

```bash
make seed
```

*Generates 20 sensors, 2000 readings, and semantic knowledge entries.*

### 3. Run Tests

Verify everything is working:

```bash
make test
```

### 4. Connect MCP Client

Add the following to your MCP settings (e.g., `cline_mcp_settings.json`):

```json
"spike-008-pgvector": {
  "command": "docker",
  "args": [
    "exec",
    "-i",
    "mcp-pgvector-server",
    "python",
    "main_server.py"
  ],
  "cwd": "/absolute/path/to/spikes/008_pgvector"
}
```

## 🛠 Tools Available

- `add_sensor(id, name, type, location)`: Register a new sensor.
- `add_reading(sensor_id, value)`: Record a reading.
- `add_knowledge(sensor_id, content)`: Add unstructured text (automatically vectorized).
- `get_readings(sensor_id, limit)`: Get recent time-series data.
- `search_knowledge(query, limit)`: Semantic search for manuals/logs.

## 🧹 Cleanup

Stop services and remove volumes (clears data):

```bash
make clean
```

