"""
Spike 008: PostgreSQL + pgvector MCP Server

This server exposes tools to interact with a PostgreSQL database enabled with pgvector.
It supports:
- Managing sensors (structured data)
- Recording readings (time-series data)
- Managing knowledge (unstructured data with vector embeddings)
- Semantic search over knowledge
"""

import logging
import os

import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pgvector_mcp")

# Initialize FastMCP
mcp = FastMCP("sensor_knowledge_base")

# Global variables for lazy loading
_model = None
_db_conn = None


def get_model():
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
            user=os.environ.get("POSTGRES_USER", "mcp_user"),
            password=os.environ.get("POSTGRES_PASSWORD", "mcp_password"),
            dbname=os.environ.get("POSTGRES_DB", "mcp_db"),
        )
        # Register pgvector type handler
        register_vector(conn)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise RuntimeError(f"Database connection failed: {e}") from e


@mcp.tool()
def add_sensor(sensor_id: str, name: str, sensor_type: str, location: str) -> str:
    """Register a new sensor in the system."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sensors (id, name, type, location) VALUES (%s, %s, %s, %s)",
                (sensor_id, name, sensor_type, location),
            )
        conn.commit()
        return f"Sensor '{name}' ({sensor_id}) added successfully."
    except psycopg2.IntegrityError:
        conn.rollback()
        return f"Error: Sensor ID '{sensor_id}' already exists."
    except Exception as e:
        conn.rollback()
        return f"Error adding sensor: {e}"
    finally:
        conn.close()


@mcp.tool()
def add_reading(sensor_id: str, value: float) -> str:
    """Record a new reading for a sensor."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if sensor exists
            cur.execute("SELECT 1 FROM sensors WHERE id = %s", (sensor_id,))
            if not cur.fetchone():
                return f"Error: Sensor ID '{sensor_id}' not found."

            cur.execute("INSERT INTO sensor_readings (sensor_id, value) VALUES (%s, %s)", (sensor_id, value))
        conn.commit()
        return f"Reading {value} recorded for {sensor_id}."
    except Exception as e:
        conn.rollback()
        return f"Error adding reading: {e}"
    finally:
        conn.close()


@mcp.tool()
def add_knowledge(sensor_id: str, content: str) -> str:
    """
    Add unstructured knowledge (manual, note, description) for a sensor.
    This will be vectorized and stored for semantic search.
    """
    conn = get_connection()
    model = get_model()

    try:
        # Generate embedding
        embedding = model.encode(content).tolist()

        with conn.cursor() as cur:
            # Check if sensor exists
            cur.execute("SELECT 1 FROM sensors WHERE id = %s", (sensor_id,))
            if not cur.fetchone():
                return f"Error: Sensor ID '{sensor_id}' not found."

            cur.execute(
                "INSERT INTO sensor_knowledge (sensor_id, content, embedding) VALUES (%s, %s, %s)",
                (sensor_id, content, embedding),
            )
        conn.commit()
        return f"Knowledge added for {sensor_id} (Embedding size: {len(embedding)})"
    except Exception as e:
        conn.rollback()
        return f"Error adding knowledge: {e}"
    finally:
        conn.close()


@mcp.tool()
def get_readings(sensor_id: str, limit: int = 10) -> str:
    """Get the most recent readings for a sensor."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT value, timestamp
                FROM sensor_readings
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """,
                (sensor_id, limit),
            )

            rows = cur.fetchall()
            if not rows:
                return f"No readings found for {sensor_id}."

            result = f"Recent readings for {sensor_id}:\n"
            for row in rows:
                result += f"- {row['timestamp']}: {row['value']}\n"
            return result
    finally:
        conn.close()


# Create an mcp to retrieve all the sensors
@mcp.tool()
def list_sensors() -> str:
    """List all registered sensors."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT id, name, type, location FROM sensors ORDER BY name ASC")
            rows = cur.fetchall()
            if not rows:
                return "No sensors registered."

            result = "Registered Sensors:\n"
            for row in rows:
                result += f"- ID: {row['id']}, Name: {row['name']}, Type: {row['type']}, Location: {row['location']}\n"
            return result
    finally:
        conn.close()


@mcp.tool()
def search_knowledge(query: str, limit: int = 5) -> str:
    """
    Perform semantic search over the sensor knowledge base.
    Finds relevant manuals, notes, or descriptions based on meaning.
    """
    conn = get_connection()
    model = get_model()

    try:
        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Perform cosine similarity search using pgvector operator <=> (distance)
            # We order by distance ASC (closest match first)
            cur.execute(
                """
                SELECT k.content, s.name as sensor_name, k.created_at,
                       (k.embedding <=> %s::vector) as distance
                FROM sensor_knowledge k
                JOIN sensors s ON k.sensor_id = s.id
                ORDER BY distance ASC
                LIMIT %s
            """,
                (query_embedding, limit),
            )

            rows = cur.fetchall()
            if not rows:
                return "No relevant knowledge found."

            result = f"Found {len(rows)} relevant items:\n"
            for row in rows:
                # Convert distance to similarity score (approximate)
                similarity = 1 - row["distance"]
                result += f"\n--- [Sensor: {row['sensor_name']}] (Similarity: {similarity:.2f}) ---\n"
                result += f"{row['content']}\n"
            return result
    except Exception as e:
        return f"Error searching knowledge: {e}"
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
