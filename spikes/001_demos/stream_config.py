"""
Run from the repository root:
    uv run spikes/001_demos/stream_config.py

This demo shows how to configure a FastMCP server with different session
persistence options and run it with the "streamable-http" transport.

To test the server, you can use the provided test client:
    uv run spikes/001_demos/try_stream_config.py

Or use the Context app and point it to the URL:
    http://127.0.0.1:8000/mcp

You will find one tool and one resource available for testing.

Origin:
    https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#streamable-http-transport
"""

import logging

from mcp.server.fastmcp import FastMCP

# Set up logging to see what's happening (reduced verbosity)
logging.basicConfig(level=logging.INFO)

# Stateful server (maintains session state)
# mcp = FastMCP("StatefulServer")

# Other configuration options:
# Stateless server (no session persistence)
# mcp = FastMCP("StatelessServer", stateless_http=True)

# Stateless server (no session persistence, no sse stream with supported client)
mcp = FastMCP("StatelessServer", stateless_http=True, json_response=True)


# Add a simple tool to demonstrate the server
@mcp.tool()
def greet(name: str = "World") -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


# Add a simple resource to test resources endpoint
@mcp.resource("example://test")
def get_test_resource() -> str:
    """Get a test resource."""
    return "This is a test resource"


# Run server with streamable-http transport (with error handling)
if __name__ == "__main__":
    print("Starting MCP server on http://127.0.0.1:8000")
    print("Server configuration: Stateless HTTP with JSON responses")
    print("Available endpoints:")
    print("  - POST http://127.0.0.1:8000/mcp for MCP protocol messages")
    print("\nExample usage:")
    print("  Test with: uv run spikes/001_demos/test_client.py")
    print("  Or use in Context with URL: http://127.0.0.1:8000/mcp")

    mcp.run(transport="streamable-http")

