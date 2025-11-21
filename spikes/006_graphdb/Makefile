# MCP Server Platform - Graph Database Spike Makefile
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

.PHONY: help up down restart rebuild logs pipeline load clean status test unit-tests

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start the GraphDB MCP platform
	@echo "Starting GraphDB MCP platform..."
	@docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "Neo4j Browser: http://localhost:7474 (neo4j/neo4jpassword)"
	@echo "MCP Server: http://localhost:8000"

down: ## Stop the platform
	@echo "🛑 Stopping platform..."
	@docker-compose down

restart: ## Restart the platform
	@echo "Restarting platform..."
	@docker-compose restart

rebuild: ## Rebuild and restart services
	@echo "Rebuilding and restarting services..."
	@docker-compose up -d --build

logs: ## Tail logs for all services
	@docker-compose logs -f

pipeline: ## Run the full data pipeline (Extract -> Embed -> Load)
	@echo "Running data pipeline..."
	@python3 pipeline/run_pipeline.py

load: ## Load data into Neo4j (runs inside container)
	@echo "Loading data into Neo4j..."
	@docker cp pipeline/load_to_neo4j.py graphdb-mcp-server:/app/load_to_neo4j.py
	@docker exec -e NEO4J_URI=bolt://neo4j:7687 graphdb-mcp-server python load_to_neo4j.py

clean: ## Clean up docker resources (volumes, containers)
	@echo "Cleaning up resources..."
	@docker-compose down -v
	@echo "✅ Cleaned up!"

status: ## Check status of containers
	@docker-compose ps

test: ## Run a simple health check
	@echo "Checking MCP server health..."
	@docker exec graphdb-mcp-server python -c "import asyncio; from main_server import get_database_stats; print(asyncio.run(get_database_stats()))"

unit-tests: ## Run unit tests
	@echo "Running unit tests..."
	@python3 -m unittest discover tests
