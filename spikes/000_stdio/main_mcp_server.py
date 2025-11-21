#!/usr/bin/env python3
"""
MCP Server Platform - spike demonstration

Run from the repository root:
    $ uv run spikes/000_stdio/main_mcp_server.py

This demo shows how to configure a FastMCP server with different session
persistence options and run it with the "stdio" transport.

This can be included in Cline


Origin:
    https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#streamable-http-transport

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

from mcp.server.fastmcp import FastMCP

# Stateful server (maintains session state)
mcp = FastMCP("StatefulServer")


# Add a simple tool to demonstrate the server
@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Add a simple resource to test resources endpoint
@mcp.resource("example://test")
def get_test_resource() -> str:
    """Get a test resource."""
    return "This is a test resource"


def main():
    """Main function to run the MCP server with error handling."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
