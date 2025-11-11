#!/usr/bin/env python3
"""
MCP Server Platform - spike 004 demonstration

Post Office MCP Server

This server manages package deliveries for multiple delivery drivers.
It provides tools to query, manage, and track packages from a CSV database.

Run with:
    $ docker-compose -f spikes/004_csv_data/docker-compose.yml run --rm mcp-server python /app/server.py

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import sys
import csv
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from uvicorn.config import LOGGING_CONFIG


# CLEAN LOGGING CONFIGURATION
def setup_clean_logging(
    level: str = "INFO",
    app_name: str = "mcp_server",
    show_uvicorn: bool = False,
    show_mcp_internals: bool = True
) -> logging.Logger:
    """Set up clean, minimal logging."""

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
    # Set handler level
    console_handler.setLevel(getattr(logging, level.upper()))

    # Use uvicorn's formatter instead of custom one
    try:
        uvicorn_formatter = logging.Formatter(
            LOGGING_CONFIG["formatters"]["default"]["fmt"],
            LOGGING_CONFIG["formatters"]["default"]["datefmt"]
        )
        console_handler.setFormatter(uvicorn_formatter)
    except (ImportError, KeyError):
        # Fallback to custom formatter if uvicorn config unavailable
        console_handler.setFormatter(formatter)

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


class PostOfficeDatabase:
    """Manages package data from CSV file."""

    def __init__(self, csv_path: str = "/app/packages.csv"):
        """Initialize the database with CSV file."""
        self.csv_path = csv_path
        self.packages: List[Dict[str, Any]] = []
        self.load_packages()

    def load_packages(self):
        """Load packages from CSV file."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        with open(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            self.packages = list(reader)

    def get_packages_for_delivery_guy(self, delivery_guy: int) -> List[Dict[str, Any]]:
        """Get all packages assigned to a specific delivery guy."""
        return [p for p in self.packages if int(p['delivery_guy']) == delivery_guy]

    def get_package_details(self, package_id: str) -> Dict[str, Any] | None:
        """Get details for a specific package."""
        for p in self.packages:
            if p['package_id'] == package_id:
                return p
        return None

    def get_delivery_guy_stats(self, delivery_guy: int) -> Dict[str, Any]:
        """Get statistics for a delivery guy."""
        packages = self.get_packages_for_delivery_guy(delivery_guy)
        total_weight = sum(float(p['weight_kg']) for p in packages)
        total_packages = len(packages)
        fragile_count = sum(1 for p in packages if p['label'] == 'FRAGILE')
        urgent_count = sum(1 for p in packages if p['label'] == 'URGENT')

        return {
            'delivery_guy': delivery_guy,
            'total_packages': total_packages,
            'total_weight_kg': round(total_weight, 2),
            'fragile_packages': fragile_count,
            'urgent_packages': urgent_count
        }

    def get_all_delivery_guys(self) -> List[int]:
        """Get all unique delivery guys."""
        guys = set(int(p['delivery_guy']) for p in self.packages)
        return sorted(list(guys))


def mcp_factory(
    app_name: str,
    logger: logging.Logger = None
) -> FastMCP:
    """Create and return a Post Office MCP server instance."""
    if logger is None:
        logger = logging.getLogger(app_name)

    # Get host and port from environment variables
    host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
    port = int(os.environ.get("FASTMCP_PORT", "8000"))

    # Create server
    mcp = FastMCP(app_name, host=host, port=port, stateless_http=True, json_response=True)

    # Initialize database
    db = PostOfficeDatabase()

    @mcp.tool()
    def get_packages_for_delivery_guy(delivery_guy: int) -> str:
        """Get all packages assigned to a specific delivery guy (1, 2, or 3)."""
        logger.info(f"Fetching packages for delivery guy {delivery_guy}")
        try:
            packages = db.get_packages_for_delivery_guy(delivery_guy)
            if not packages:
                return f"No packages found for delivery guy {delivery_guy}"

            result = f"Packages for Delivery Guy {delivery_guy}:\n"
            for pkg in packages:
                result += f"\nPackage {pkg['package_id']}:\n"
                result += f"  Label: {pkg['label']}\n"
                result += f"  Weight: {pkg['weight_kg']} kg\n"
                result += f"  Size: {pkg['size_cm']}\n"
                result += f"  From: {pkg['sender_name']} ({pkg['sender_address']})\n"
                result += f"  To: {pkg['receiver_name']} ({pkg['receiver_address']})\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching packages: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_package_details(package_id: str) -> str:
        """Get detailed information for a specific package."""
        logger.info(f"Fetching details for package {package_id}")
        try:
            pkg = db.get_package_details(package_id)
            if not pkg:
                return f"Package {package_id} not found"

            result = f"Package Details: {package_id}\n"
            result += f"Assigned to: Delivery Guy {pkg['delivery_guy']}\n"
            result += f"Label: {pkg['label']}\n"
            result += f"Weight: {pkg['weight_kg']} kg\n"
            result += f"Size: {pkg['size_cm']}\n"
            result += f"\nSender:\n"
            result += f"  Name: {pkg['sender_name']}\n"
            result += f"  Address: {pkg['sender_address']}\n"
            result += f"\nReceiver:\n"
            result += f"  Name: {pkg['receiver_name']}\n"
            result += f"  Address: {pkg['receiver_address']}\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching package details: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_delivery_guy_stats(delivery_guy: int) -> str:
        """Get delivery statistics for a specific delivery guy."""
        logger.info(f"Fetching stats for delivery guy {delivery_guy}")
        try:
            stats = db.get_delivery_guy_stats(delivery_guy)
            result = f"Delivery Statistics - Guy {delivery_guy}:\n"
            result += f"Total Packages: {stats['total_packages']}\n"
            result += f"Total Weight: {stats['total_weight_kg']} kg\n"
            result += f"Fragile Packages: {stats['fragile_packages']}\n"
            result += f"Urgent Packages: {stats['urgent_packages']}\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_all_delivery_guys() -> str:
        """Get list of all delivery guys in the system."""
        logger.info("Fetching list of all delivery guys")
        try:
            guys = db.get_all_delivery_guys()
            result = "Available Delivery Guys: " + ", ".join(str(g) for g in guys)
            return result
        except Exception as e:
            logger.error(f"Error fetching delivery guys: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def search_packages_by_label(label: str) -> str:
        """Search packages by label type (FRAGILE, STANDARD, URGENT)."""
        logger.info(f"Searching packages with label: {label}")
        try:
            matching = [p for p in db.packages if p['label'] == label.upper()]
            if not matching:
                return f"No packages found with label: {label}"

            result = f"Packages with label '{label}':\n"
            for pkg in matching:
                result += f"\n{pkg['package_id']} - Delivery Guy {pkg['delivery_guy']}\n"
                result += f"  State: {pkg['state']}\n"
                result += f"  Weight: {pkg['weight_kg']} kg\n"
                result += f"  To: {pkg['receiver_name']}\n"
            return result
        except Exception as e:
            logger.error(f"Error searching packages: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_packages_by_state(state: str) -> str:
        """Get all packages with a specific state (pending, delivered, in_transit)."""
        logger.info(f"Fetching packages with state: {state}")
        try:
            matching = [p for p in db.packages if p['state'].lower() == state.lower()]
            if not matching:
                return f"No packages found with state: {state}"

            result = f"Packages with state '{state}':\n"
            for pkg in matching:
                result += f"\n{pkg['package_id']} - Delivery Guy {pkg['delivery_guy']}\n"
                result += f"  Label: {pkg['label']}\n"
                result += f"  Weight: {pkg['weight_kg']} kg\n"
                result += f"  To: {pkg['receiver_name']}\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching packages by state: {e}")
            return f"Error: {e}"
        
    @mcp.tool()
    def update_package_state(package_id: str, new_state: str) -> str:
        """Update the state of a specific package."""
        logger.info(f"Updating state for package {package_id} to {new_state}")
        try:
            pkg = db.get_package_details(package_id)
            if not pkg:
                return f"Package {package_id} not found"

            old_state = pkg['state']
            pkg['state'] = new_state

            # Save changes back to CSV
            with open(db.csv_path, 'w', newline='') as f:
                fieldnames = pkg.keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(db.packages)

            return f"Package {package_id} state updated from {old_state} to {new_state}"
        except Exception as e:
            logger.error(f"Error updating package state: {e}")
            return f"Error: {e}"
    
    @mcp.tool()
    def add_new_package(package_data: Dict[str, Any]) -> str:
        """Add a new package to the database."""
        logger.info(f"Adding new package with ID {package_data.get('package_id')}")
        try:
            db.packages.append(package_data)

            # Save changes back to CSV
            with open(db.csv_path, 'w', newline='') as f:
                fieldnames = package_data.keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(db.packages)

            return f"Package {package_data.get('package_id')} added successfully"
        except Exception as e:
            logger.error(f"Error adding new package: {e}")
            return f"Error: {e}"
        
    @mcp.tool()
    def delete_package(package_id: str) -> str:
        """Delete a package from the database."""
        logger.info(f"Deleting package with ID {package_id}")
        try:
            pkg = db.get_package_details(package_id)
            if not pkg:
                return f"Package {package_id} not found"

            db.packages.remove(pkg)

            # Save changes back to CSV
            with open(db.csv_path, 'w', newline='') as f:
                fieldnames = pkg.keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(db.packages)

            return f"Package {package_id} deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting package: {e}")
            return f"Error: {e}"
    
    @mcp.tool()
    def delete_packages(package_ids: List[str]) -> str:
        """Delete multiple packages from the database."""
        logger.info(f"Deleting multiple packages with IDs: {package_ids}")
        try:
            deleted_count = 0
            for package_id in package_ids:
                pkg = db.get_package_details(package_id)
                if pkg:
                    db.packages.remove(pkg)
                    deleted_count += 1

            # Save changes back to CSV
            if deleted_count > 0:
                with open(db.csv_path, 'w', newline='') as f:
                    fieldnames = db.packages[0].keys() if db.packages else []
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(db.packages)

            return f"Deleted {deleted_count} packages successfully"
        except Exception as e:
            logger.error(f"Error deleting multiple packages: {e}")
            return f"Error: {e}"

    return mcp

  


def main(app_name: str = "post_office_server"):
    """Run the server with clean logging."""
    logger = setup_clean_logging(level="DEBUG", app_name=app_name)

    # Get configured host and port
    host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
    port = int(os.environ.get("FASTMCP_PORT", "8000"))

    logger.info("🚀 Starting Post Office MCP Server")
    logger.info(f"📍 Endpoint: http://{host}:{port}/mcp")
    logger.info("🔧 Tools: get_packages_for_delivery_guy, get_package_details, get_delivery_guy_stats, get_all_delivery_guys, search_packages_by_label")
    logger.info("📦 Database: Loading packages from CSV")

    try:
        mcp = mcp_factory(app_name=app_name, logger=logger)
        # FastMCP with stateless_http=True runs as HTTP server
        # Call run() without transport parameter - it will use HTTP automatically with stateless_http=True
        mcp.run()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        if "ClosedResourceError" in str(e):
            logger.warning("⚠️  Client disconnected unexpectedly - continuing")
        else:
            logger.error(f"❌ Server error: {e}")
            raise


if __name__ == "__main__":
    main()
