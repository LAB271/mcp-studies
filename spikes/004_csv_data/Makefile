# MCP Server Platform - Post Office Local Deployment Makefile
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

LOCAL_DOMAIN = mcp.local
GATEWAY = https://$(LOCAL_DOMAIN)


.PHONY: help setup generate-certs start stop restart logs clean status test

start: ## Start Colima if not already running
	@colima start
	@colima status

.ssl-certs/nginx.crt: 
	@mkdir -p .ssl-certs
	@if ! grep -q "$(LOCAL_DOMAIN)" /etc/hosts 2>/dev/null; then \
		echo "127.0.0.1 $(LOCAL_DOMAIN)" | sudo tee -a /etc/hosts > /dev/null 2>&1 || echo "⚠️  Note: Could not add $(LOCAL_DOMAIN) to /etc/hosts. You may need to add it manually or use localhost."; \
	fi
	@mkcert -key-file .ssl-certs/nginx.key -cert-file .ssl-certs/nginx.crt $(LOCAL_DOMAIN) 2>/dev/null || mkcert -key-file .ssl-certs/nginx.key -cert-file .ssl-certs/nginx.crt localhost 127.0.0.1


up: .ssl-certs/nginx.crt
	@echo "Starting MCP platform..."
	@docker-compose -f docker-compose.yml up -d --build
	@echo ""
	@echo "✅ Services started!"

down:  ## Stop MCP platform
	@echo "🛑 Stopping MCP platform..."
	@docker-compose -f docker-compose.yml down

clean: clean-certs ## Clean up docker
	@docker-compose -f docker-compose.yml down -v
	@docker images | grep "localhost:" | awk '{print $$3}' | xargs docker rmi -f || true
	@docker rm -f $$(docker ps -aq) || true
	@docker rmi -f $$(docker images -aq) || true
	@docker volume prune -f || true
	@docker network prune -f || true
	@docker system prune -a -f --volumes|| true

restart: ## Restart MCP platform
	@echo "Restarting MCP platform..."
	@docker-compose -f docker-compose.yml restart

rebuild: ## Rebuild MCP platform
	@echo "Rebuilding and restarting services..."
	@docker-compose -f docker-compose.yml up -d --build

logs: ## Tail logs for all services
	@docker-compose -f docker-compose.yml logs -f

logs-nginx: ## Tail logs for nginx-gateway service
	@docker-compose -f docker-compose.yml logs -f nginx-gateway

logs-app: ## Tail logs for mcp-server service
	@docker-compose -f docker-compose.yml logs -f mcp-server

status:
	@echo "Service Status:"
	@docker-compose -f docker-compose.yml ps
	@echo ""
	@echo "Network Status:"
	@docker network inspect 004_csv_data_mcp-network-post-office 2>/dev/null | grep -A 5 "Containers" || echo "Network not found"

clean-certs:
	@echo "Removing SSL certificates..."
	@rm -rf .ssl-certs
	@echo "✓ Certificates removed"

.DEFAULT_GOAL := help
help: ## Shows help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "\033[33mAccess URLs:\033[0m"
	@echo "  Gateway:   $(GATEWAY)"
	@echo ""
	@echo "Run 'make logs' to view logs"
