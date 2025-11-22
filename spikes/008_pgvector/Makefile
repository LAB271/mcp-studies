# Spike 008: PostgreSQL + pgvector
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

.PHONY: help up down clean logs restart shell test

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start the services (Postgres + MCP Server)
	@echo "Starting Spike 008 services..."
	@docker-compose up -d --build
	@echo "✅ Services started! Postgres is on port 5432."

down: ## Stop the services
	@echo "🛑 Stopping services..."
	@docker-compose down

clean: ## Stop services and remove volumes (WARNING: Deletes DB data)
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@echo "✅ Cleaned."

logs: ## View logs
	@docker-compose logs -f

restart: down up ## Restart services

rebuild: ## Rebuild and restart services
	@echo "Rebuilding services..."
	@docker-compose up -d --build
	@echo "✅ Services rebuilt and started!"

shell: ## Open a shell in the MCP server container
	@docker-compose exec mcp-server /bin/bash

test: ## Run the test suite
	@echo "🧪 Running tests..."
	@# We run tests inside the container to ensure environment consistency
	@docker-compose exec mcp-server python -m pytest test_008_pgvector.py

seed: ## Generate mock data
	@echo "🌱 Seeding database with mock data..."
	@docker-compose exec mcp-server python generate_data.py

