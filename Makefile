# MCP Server Platform - Local Deployment Makefile
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

check: ## Validate primary development dependencies
	@uv --version > /dev/null && echo "✅ uv available" || (echo "❌ Please install uv as package manager: https://docs.astral.sh/uv/" && exit 1)

test: ## Run tests
	@uv run -m pytest

lint: ## Run linting and formatting checks
	@echo "🔍 Running ruff linting..."
	@uv run ruff check .
	@echo "🎨 Running ruff formatting check..."
	@uv run ruff format --check .
	@echo "✅ All linting checks passed!"

format: ## Format code with ruff
	@echo "🎨 Formatting code with ruff..."
	@uv run ruff format .
	@echo "✅ Code formatted!"

lint-fix: ## Fix linting issues automatically
	@echo "🔧 Fixing linting issues with ruff..."
	@uv run ruff check --fix .
	@uv run ruff format .
	@echo "✅ Linting issues fixed!"

env: ## setup the development environment
	@uv venv --clear
	@uv sync
# 	@uv sync --group dev
# 	@.env.sh || (echo "❌ Failed to create .env file. Please ensure 1Password CLI is installed and configured." && exit 1)
	@echo "✅ Development environment is set up. Activate it with: source .venv/bin/activate"

clean: ## Clean up environment
	@rm -rf .venv
	@rm -f .env	
	@find . -name *.pyc -delete
	@rm -f uv.lock
	@rm -frd .pytest_cache .ruff_cache .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} +

.DEFAULT_GOAL := help
help: ## Shows help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'