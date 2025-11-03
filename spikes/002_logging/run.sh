#!/bin/bash

# MCP Server Platform - spike runner
# Copyright (c) 2025 LAB271
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
uv run "$SCRIPT_DIR/main_server.py"

# Test the server with:
# curl -H "Accept: text/event-stream" http://localhost:8000/mcp
# Or for JSON response:
# curl -s -H "Accept: application/json" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' http://localhost:8000/mcp