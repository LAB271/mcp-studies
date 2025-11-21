# MCP Server Platform - Postgres Spike Makefile
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

.PHONY: help up down restart rebuild logs clean unit-tests

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

unit-tests: ## Run unit tests
	@echo "Running unit tests..."
	@python3 -m unittest discover -v tests

up: ## Start the Postgres MCP platform
	@echo "Starting Postgres MCP platform..."
	@docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "MCP Server: http://localhost:8000 (if exposed)"

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

clean: ## Clean up docker resources (volumes, containers)
	@echo "Cleaning up resources..."
	@docker-compose down -v
	@echo "✅ Cleaned up!"
