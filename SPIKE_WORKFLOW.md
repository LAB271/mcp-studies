# Spike Creation Workflow

This document outlines the standard workflow for creating new MCP spikes in this repository. Follow these steps to ensure consistency, quality, and ease of testing.

## 1. Preparation

Start by creating a new branch and directory for the spike.

```bash
# 1. Create a new branch
git checkout -b spike-XXX

# 2. Create the spike directory
mkdir spikes/XXX_name
cd spikes/XXX_name
```

## 2. Definition

Define what the spike will do. Create a `README.md` in the spike directory.

* **Goals**: What are we trying to prove or demonstrate?
* **Structure**: What files will be created?
* **Usage**: How do we run it?

## 3. Infrastructure

Set up the environment using Docker.

* **`docker-compose.yml`**: Define the services (e.g., Database, MCP Server).
* **`Dockerfile`**: If a custom image is needed for the server.
* **Support Files**: `init.sql`, `requirements.txt`, etc.

## 4. Implementation

Write the MCP server logic.

* **`main_server.py`**: The core Python script using `FastMCP`.
* **Tools**: Define the tools (`@mcp.tool()`) that expose functionality.
* **Resources**: Define resources (`@mcp.resource()`) if applicable.
* **Prompts**: Define prompts (`@mcp.prompt()`) if applicable.

## 5. Automation

Create a `Makefile` in the spike directory to standardize commands.

Standard targets:

* `up`: Start services (`docker-compose up -d`).
* `down`: Stop services.
* `logs`: Tail logs.
* `clean`: Remove volumes and containers.
* `unit-tests`: Run the test suite.

## 6. Quality Assurance (Testing)

Ensure the code works without requiring the full infrastructure to be running.

1. Create a `tests/` directory.
2. Create `test_main_server.py`.
3. **Mock Dependencies**: Use `unittest.mock` to mock external libraries (like `psycopg2`, `neo4j`, `requests`) and the `FastMCP` framework itself.
4. Verify that `make unit-tests` passes.

## 7. Integration

Configure the MCP client to test the server.

* **Cline**: Update `cline_mcp_settings.json` (usually in `~/.config/...` or VS Code storage).
  * Add the new server configuration.
  * Use `stdio` transport.
  * Use `uv run` or `docker exec` commands.
* **Inspector**: Verify using `npx @modelcontextprotocol/inspector`.

## 8. Delivery

Commit and push the changes.

```bash
# 1. Stage changes
git add .

# 2. Commit
git commit -m "feat(spike-XXX): description of the spike"

# 3. Push
git push origin spike-XXX

# 4. Create Pull Request
gh pr create --title "feat(spike-XXX): Title" --body "Description..."
```
