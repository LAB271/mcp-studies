#!/usr/bin/env python3
"""
MCP Server Platform - spike demonstration

Run from the repository root:
    $ uv run spikes/001_demos/main_mcp_server.py

This demo shows how to configure a FastMCP server with different session
persistence options and run it with the "streamable-http" transport.

To test the server, you can use the provided test client:
    $ uv run spikes/001_demos/try_stream_config.py

Or use the Context app and point it to the URL:
    http://127.0.0.1:8000/mcp

You will find one tool and one resource available for testing.

Origin:
    https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#streamable-http-transport

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

from mcp.server.fastmcp import FastMCP

# Stateful server (maintains session state)
# mcp = FastMCP("StatefulServer")

# Other configuration options:
# Stateless server (no session persistence)
# mcp = FastMCP("StatelessServer", stateless_http=True)

# Stateless server (no session persistence, no sse stream with supported client)
mcp = FastMCP("StatelessServer", stateless_http=True, json_response=True)


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
    print("Starting MCP server on http://127.0.0.1:8000")
    print("Server configuration: Stateless HTTP with JSON responses")
    print("Available endpoints:")
    print("  - POST http://127.0.0.1:8000/mcp for MCP protocol messages")
    print("\nAvailable features:")
    print("  🔧 Tools: greet")
    print("  📝 Prompts: simple_greeting_prompt")
    print("  📄 Resources: example://test")
    print("\nExample usage:")
    print("  Test with: uv run spikes/001_demos/test_client.py")
    print("  Or use in Context with URL: http://127.0.0.1:8000/mcp")

    mcp.run(transport="streamable-http")


# Run server with streamable-http transport (with error handling)
if __name__ == "__main__":  # pragma: no cover
    main()
