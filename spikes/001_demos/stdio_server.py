"""
Working MCP server using stdio transport for testing
"""

from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("TestServer")


@mcp.tool()
def greet(name: str = "World") -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@mcp.resource("example://test")
def get_test_resource() -> str:
    """Get a test resource."""
    return "This is a test resource"


if __name__ == "__main__":
    # Use stdio transport which is known to work
    mcp.run(transport="stdio")
