"""
Logging Configuration Module

Use this to harmonize logging across all your MCP servers.
Import and call setup_logging() at the start of your server scripts.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    app_name: str = "mcp_server",
    show_uvicorn: bool = False,
    show_mcp_internals: bool = False
) -> logging.Logger:
    """
    Set up clean, harmonized logging for MCP servers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        app_name: Name for your application logger
        show_uvicorn: Whether to show uvicorn HTTP access logs
        show_mcp_internals: Whether to show internal MCP protocol logs
        
    Returns:
        Logger instance for your application
    """
    
    # Custom formatter for clean output
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
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
    app_logger.setLevel(getattr(logging, level.upper()))
    
    return app_logger


def create_quiet_server_logger(name: str = "server") -> logging.Logger:
    """Create a logger for production servers with minimal output."""
    return setup_logging(
        level="INFO",
        app_name=name,
        show_uvicorn=False,
        show_mcp_internals=False
    )


def create_debug_server_logger(name: str = "debug_server") -> logging.Logger:
    """Create a logger for debugging with more verbose output."""
    return setup_logging(
        level="DEBUG", 
        app_name=name,
        show_uvicorn=True,
        show_mcp_internals=True
    )


# Example usage patterns
if __name__ == "__main__":
    # Demo different logging configurations
    print("=== QUIET LOGGING ===")
    quiet_logger = create_quiet_server_logger("quiet_demo")
    quiet_logger.info("This is clean, minimal logging")
    quiet_logger.warning("Only important messages show")
    
    print("\n=== DEBUG LOGGING ===")
    debug_logger = create_debug_server_logger("debug_demo")
    debug_logger.debug("This shows debug information")
    debug_logger.info("More verbose for development")
    
    print("\n=== CUSTOM LOGGING ===")
    custom_logger = setup_logging(
        level="WARNING",
        app_name="custom",
        show_uvicorn=False,
        show_mcp_internals=False
    )
    custom_logger.warning("Custom configuration example")