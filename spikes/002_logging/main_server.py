#!/usr/bin/env python3
"""
MCP Server Platform - spike demonstration

Clean MCP Server with Harmonized Logging

This version has clean, organized logging with minimal noise.
Only shows what you actually need to see.

Run with:
    $ uv run spikes/002_logging/main_server.py

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP
from uvicorn.config import LOGGING_CONFIG


# CLEAN LOGGING CONFIGURATION
def setup_clean_logging(
    level: str = "INFO", app_name: str = "mcp_server", show_uvicorn: bool = False, show_mcp_internals: bool = True
) -> logging.Logger:
    """Set up clean, minimal logging."""

    # Custom formatter for clean output
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)8s] %(name)s: %(message)s", datefmt="%H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    # Set handler level
    console_handler.setLevel(getattr(logging, level.upper()))

    # Use uvicorn's formatter instead of custom one
    try:
        uvicorn_formatter = logging.Formatter(
            LOGGING_CONFIG["formatters"]["default"]["fmt"], LOGGING_CONFIG["formatters"]["default"]["datefmt"]
        )
        console_handler.setFormatter(uvicorn_formatter)
    except (ImportError, KeyError):
        # Fallback to custom formatter if uvicorn config unavailable
        console_handler.setFormatter(formatter)  # pragma: no cover

    # root_logger.addHandler(console_handler)

    # SILENCE NOISY COMPONENTS
    noise_loggers = {
        "uvicorn": logging.WARNING if not show_uvicorn else logging.INFO,
        "uvicorn.access": logging.WARNING if not show_uvicorn else logging.INFO,
        "uvicorn.error": logging.WARNING,
        "mcp.server.lowlevel.server": logging.WARNING if not show_mcp_internals else logging.INFO,
        "mcp.server.streamable_http": logging.WARNING if not show_mcp_internals else logging.INFO,
        "mcp.server.streamable_http_manager": logging.WARNING if not show_mcp_internals else logging.INFO,
        "anyio": logging.WARNING,
        "anyio.abc": logging.ERROR,
        "anyio.streams": logging.ERROR,
        "sse_starlette": logging.WARNING,
    }

    for logger_name, log_level in noise_loggers.items():
        logging.getLogger(logger_name).setLevel(log_level)

    # Create and return application logger
    app_logger = logging.getLogger(app_name)
    app_logger.handlers = root_logger.handlers
    app_logger.setLevel(getattr(logging, level.upper()))

    return app_logger


def mcp_factory(app_name: str, logger: logging.Logger = None) -> FastMCP:
    """Create and return a Clean MCP server instance."""
    if logger is None:
        logger = logging.getLogger(app_name)

    # Create server
    mcp = FastMCP(app_name, stateless_http=True, json_response=True)

    @mcp.tool()
    def greet(name: str = "World") -> str:
        """Greet someone by name."""
        logger.info(f"Greeting {name}")
        return f"Hello, {name}!"

    @mcp.tool()
    def calculate(expression: str) -> str:
        """Safely calculate a simple math expression."""
        try:
            # Only allow basic math operations for safety
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic math operations allowed"

            result = eval(expression)
            logger.info(f"Calculated: {expression} = {result}")
            return f"{expression} = {result}"
        except Exception as e:
            logger.warning(f"Calculation error: {e}")
            return f"Error: {e}"

    @mcp.prompt()
    def greet_user(name: str, style: str = "friendly") -> str:
        """Generate a greeting prompt"""
        styles = {
            "friendly": "Please write a warm, friendly greeting",
            "formal": "Please write a formal, professional greeting",
            "casual": "Please write a casual, relaxed greeting",
        }

        return f"{styles.get(style, styles['friendly'])} for someone named {name}."

    @mcp.resource("server://info")
    def get_server_info() -> str:
        """Get server information."""
        logger.info("Server info requested")
        return """Clean MCP Server
    - Minimal logging
    - Basic tools available
    - Ready for development"""

    return mcp


def main(app_name: str = "clean_server"):
    """Run the server with clean logging."""
    logger = setup_clean_logging(level="DEBUG", app_name=app_name)

    logger.info("🚀 Starting Clean MCP Server")
    logger.info("📍 Endpoint: http://127.0.0.1:8000/mcp")
    logger.info("🔧 Tools: greet, calculate")
    logger.info("📄 Resources: server://info")

    try:
        mcp = mcp_factory(app_name=app_name, logger=logger)
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        if "ClosedResourceError" in str(e):
            logger.warning("⚠️  Client disconnected unexpectedly - continuing")
        else:
            logger.error(f"❌ Server error: {e}")
            raise  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    main()
