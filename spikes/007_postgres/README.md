# Spike 007: PostgreSQL MCP Server

This spike demonstrates how to build a Model Context Protocol (MCP) server that interfaces with a PostgreSQL database.

## Goals
- Run a PostgreSQL database in Docker.
- Create an MCP server that can:
    - List tables.
    - Get table schema.
    - Execute read-only SQL queries.
    - (Optional) Perform specific business logic queries.
- Demonstrate secure connection and configuration.

## Structure
- `main_server.py`: The MCP server implementation.
- `docker-compose.yml`: Orchestration for Postgres and the MCP server.
- `init.sql`: Initial database schema and data.

## Usage

1. **Start the environment**:
   ```bash
   make up
   ```

2. **Test with MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector python main_server.py
   ```
