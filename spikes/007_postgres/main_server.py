import logging
import os

import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("postgres_mcp")

# Initialize FastMCP
mcp = FastMCP("postgres_explorer")

def get_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
            user=os.environ.get("POSTGRES_USER", "mcp_user"),
            password=os.environ.get("POSTGRES_PASSWORD", "mcp_password"),
            dbname=os.environ.get("POSTGRES_DB", "mcp_db")
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise RuntimeError(f"Database connection failed: {e}") from e

@mcp.tool()
def list_tables() -> str:
    """List all tables in the public schema."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            return f"Tables in database: {', '.join(tables)}"
    finally:
        conn.close()

@mcp.tool()
def describe_table(table_name: str) -> str:
    """Get the schema information for a specific table."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Check if table exists to avoid SQL injection in the next query if we were concatenating
            # But here we use parameters for the schema query
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

            rows = cur.fetchall()
            if not rows:
                return f"Table '{table_name}' not found or has no columns."

            result = f"Schema for table '{table_name}':\n"
            for row in rows:
                result += f"- {row['column_name']} ({row['data_type']})"
                if row['is_nullable'] == 'YES':
                    result += " [NULLABLE]"
                result += "\n"
            return result
    finally:
        conn.close()

@mcp.tool()
def execute_read_query(query: str) -> str:
    """
    Execute a read-only SQL query.
    WARNING: This tool assumes the database user has appropriate permissions.
    Only SELECT queries should be allowed by the user logic, but this executes raw SQL.
    """
    if not query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for safety."

    conn = get_connection()
    try:
        # Set session to read-only just in case
        conn.set_session(readonly=True)

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query)

            # Fetch results
            rows = cur.fetchall()
            if not rows:
                return "Query returned no results."

            # Format as string (simple representation)
            result = f"Query returned {len(rows)} rows:\n"

            # Get headers
            headers = [desc[0] for desc in cur.description]
            result += " | ".join(headers) + "\n"
            result += "-" * (len(result.split('\n')[-1])) + "\n"

            for row in rows:
                # Convert all values to string
                values = [str(val) for val in row]
                result += " | ".join(values) + "\n"

            return result
    except Exception as e:
        return f"Query execution error: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()
