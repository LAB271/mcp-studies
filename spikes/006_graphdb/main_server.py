#!/usr/bin/env python3
"""
MCP Server Platform - spike 006 Graph Database

Vector Database MCP Server

This server provides tools to query a Neo4j graph database containing
documents, embeddings, and chunks for semantic search and retrieval.

Run with:
    $ docker-compose -f spikes/006_graphdb/docker-compose.yml run --rm graphdb-mcp-server python /app/server.py

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

import logging
import os
import sys
from typing import Any

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


class GraphDatabase:
    """Manages Neo4j graph database connections and queries."""

    def __init__(self, host: str = "neo4j", port: int = 7687, user: str = "neo4j", password: str = "neo4jpassword"):
        """Initialize database connection settings (lazy connection)."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.driver = None
        self.session = None
        self.Neo4jDriver = None

    def connect(self):
        """Establish connection to Neo4j (lazy initialization)."""
        if self.driver is not None:
            return
        
        try:
            from neo4j import GraphDatabase as Neo4jDriver
            self.Neo4jDriver = Neo4jDriver
            self.driver = Neo4jDriver.driver(f"bolt://{self.host}:{self.port}", auth=(self.user, self.password))
        except ImportError as e:
            raise ImportError("neo4j package not installed") from e
        except Exception as e:
            raise Exception(f"Failed to connect to Neo4j at {self.host}:{self.port}: {e}") from e

    def get_session(self):
        """Get or create a session."""
        self.connect()
        if self.session is None:
            self.session = self.driver.session(database="neo4j")
        return self.session

    def query(self, cypher_query: str, **params) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results."""
        session = self.get_session()
        try:
            result = session.run(cypher_query, **params)
            return [dict(record) for record in result]
        except Exception as e:
            raise Exception(f"Database query failed: {e}") from e

    def get_all_documents(self) -> list[dict[str, Any]]:
        """Get all documents from the database."""
        query = "MATCH (d:Document) RETURN d.id as id, d.title as title, d.type as type, d.size_bytes as size"
        return self.query(query)

    def search_chunks(self, search_text: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search for chunks containing specific text."""
        query = """
        MATCH (c:Chunk) 
        WHERE c.text CONTAINS $text 
        RETURN c.text as text, c.position as position 
        LIMIT $limit
        """
        return self.query(query, text=search_text, limit=limit)

    def get_document_chunks(self, document_title: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get chunks from a specific document."""
        query = """
        MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
        WHERE d.title = $title
        RETURN c.text as text, c.position as position
        LIMIT $limit
        """
        return self.query(query, title=document_title, limit=limit)

    def get_database_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        try:
            docs = self.query("MATCH (d:Document) RETURN COUNT(d) as count")
            chunks = self.query("MATCH (c:Chunk) RETURN COUNT(c) as count")
            rels = self.query("MATCH ()-[r:CONTAINS]->() RETURN COUNT(r) as count")
            
            return {
                "documents": docs[0]["count"] if docs else 0,
                "chunks": chunks[0]["count"] if chunks else 0,
                "relationships": rels[0]["count"] if rels else 0
            }
        except Exception:
            return {"documents": 0, "chunks": 0, "relationships": 0}

    def search_by_keywords(self, keywords: list[str], limit: int = 5) -> list[dict[str, Any]]:
        """Search chunks containing any of the keywords."""
        if not keywords:
            return []
        conditions = " OR ".join([f"c.text CONTAINS '{kw}'" for kw in keywords])
        query = f"MATCH (c:Chunk) WHERE {conditions} RETURN c.text as text, c.position as position LIMIT {limit}"
        return self.query(query)

    def get_embeddings_info(self) -> dict[str, Any]:
        """Get information about embeddings in the database."""
        return {
            "embedding_files": ["ps2man_embeddings.json", "ps3man_embeddings.json", "ic_datasheets_reference_embeddings.json"],
            "total_files": 3
        }

    def close(self):
        """Close database connection."""
        if self.session:
            self.session.close()
        if self.driver:
            self.driver.close()


def mcp_factory(
    app_name: str,
    logger: logging.Logger = None
) -> FastMCP:
    """Create and return a Graph Database MCP server instance."""
    if logger is None:
        logger = logging.getLogger(app_name)

    # Check for stdio mode
    if os.environ.get("MCP_TRANSPORT") == "stdio":
        mcp = FastMCP(app_name)
    else:
        # Get host and port from environment variables
        host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
        port = int(os.environ.get("FASTMCP_PORT", "8000"))

        # Create server
        mcp = FastMCP(app_name, host=host, port=port, stateless_http=True, json_response=True)

    # Initialize database
    neo4j_host = os.environ.get("NEO4J_HOST", "neo4j")
    neo4j_port = int(os.environ.get("NEO4J_PORT", "7687"))
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "neo4jpassword")

    db = GraphDatabase(host=neo4j_host, port=neo4j_port, user=neo4j_user, password=neo4j_password)

    @mcp.tool()
    def get_all_documents() -> str:
        """Get all documents in the graph database."""
        logger.info("Fetching all documents")
        try:
            documents = db.get_all_documents()
            if not documents:
                return "No documents found in database"

            result = "Documents in Database:\n"
            for doc in documents:
                result += f"\n{doc['title']} ({doc['type']})\n"
                result += f"  ID: {doc['id']}\n"
                if doc['size']:
                    result += f"  Size: {doc['size']} bytes\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def search_chunks(query: str, limit: int = 5) -> str:
        """Search for chunks containing specific text."""
        logger.info(f"Searching for chunks containing: {query}")
        try:
            chunks = db.search_chunks(query, limit)
            if not chunks:
                return f"No chunks found containing '{query}'"

            result = f"Found {len(chunks)} chunks containing '{query}':\n"
            for i, chunk in enumerate(chunks, 1):
                text = chunk['text'][:150] + "..." if len(chunk['text']) > 150 else chunk['text']
                result += f"\n{i}. Position {chunk['position']}:\n   {text}\n"
            return result
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_document_chunks(document_title: str, limit: int = 10) -> str:
        """Get all chunks from a specific document."""
        logger.info(f"Fetching chunks from document: {document_title}")
        try:
            chunks = db.get_document_chunks(document_title, limit)
            if not chunks:
                return f"No chunks found for document '{document_title}'"
            
            result = f"Chunks from '{document_title}' (showing {len(chunks)} of available):\n"
            for i, chunk in enumerate(chunks, 1):
                text = chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text']
                result += f"\n{i}. Position {chunk['position']}:\n   {text}\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching document chunks: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_database_stats() -> str:
        """Get statistics about the graph database."""
        logger.info("Fetching database statistics")
        try:
            stats = db.get_database_stats()
            result = "Graph Database Statistics:\n"
            result += f"Total Documents: {stats['documents']}\n"
            result += f"Total Chunks: {stats['chunks']}\n"
            result += f"Document-Chunk Relationships: {stats['relationships']}\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching database stats: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def search_by_keywords(keywords: str, limit: int = 5) -> str:
        """Search chunks containing any of the provided keywords (comma-separated)."""
        logger.info(f"Searching for keywords: {keywords}")
        try:
            keyword_list = [kw.strip() for kw in keywords.split(",")]
            chunks = db.search_by_keywords(keyword_list, limit)
            if not chunks:
                return f"No chunks found containing any of: {keywords}"
            
            result = f"Found {len(chunks)} chunks containing keywords:\n"
            for i, chunk in enumerate(chunks, 1):
                text = chunk['text'][:150] + "..." if len(chunk['text']) > 150 else chunk['text']
                result += f"\n{i}. Position {chunk['position']}:\n   {text}\n"
            return result
        except Exception as e:
            logger.error(f"Error searching keywords: {e}")
            return f"Error: {e}"

    @mcp.tool()
    def get_embeddings_info() -> str:
        """Get information about embeddings in the database."""
        logger.info("Fetching embeddings information")
        try:
            info = db.get_embeddings_info()
            result = "Embeddings Information:\n"
            result += f"Total Embedding Files: {info['total_files']}\n"
            result += "Files:\n"
            for file in info['embedding_files']:
                result += f"  - {file}\n"
            return result
        except Exception as e:
            logger.error(f"Error fetching embeddings info: {e}")
            return f"Error: {e}"

    return mcp


def main(app_name: str = "graph_database_server"):
    """Run the server with clean logging."""
    logger = setup_clean_logging(level="DEBUG", app_name=app_name)

    # Get configured host and port
    host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
    port = int(os.environ.get("FASTMCP_PORT", "8000"))

    logger.info("🚀 Starting Graph Database MCP Server")
    logger.info(f"📍 Endpoint: http://{host}:{port}/mcp")
    logger.info("🔧 Tools: get_all_documents, search_chunks, get_document_chunks, get_database_stats, search_by_keywords, get_embeddings_info")
    logger.info("📊 Database: Lazy connection - will connect on first use")

    try:
        mcp = mcp_factory(app_name=app_name, logger=logger)
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
