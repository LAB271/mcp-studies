import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Save original modules to restore later
original_modules = {
    "mcp.server.fastmcp": sys.modules.get("mcp.server.fastmcp"),
    "psycopg2": sys.modules.get("psycopg2"),
    "psycopg2.extras": sys.modules.get("psycopg2.extras"),
}

# Mock dependencies before importing main_server
mock_mcp_module = MagicMock()
sys.modules["mcp.server.fastmcp"] = mock_mcp_module
sys.modules["psycopg2"] = MagicMock()
sys.modules["psycopg2.extras"] = MagicMock()

# Configure FastMCP to act as a pass-through decorator
# This ensures that @mcp.tool() doesn't replace the function with a Mock
def tool_decorator_factory(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

mock_mcp_instance = MagicMock()
mock_mcp_instance.tool.side_effect = tool_decorator_factory
mock_mcp_module.FastMCP.return_value = mock_mcp_instance

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

try:
    main_server = load_spike_module("007_postgres", "main_server")
    describe_table = main_server.describe_table
    execute_read_query = main_server.execute_read_query
    list_tables = main_server.list_tables
finally:
    # Restore original modules
    for name, original in original_modules.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original


class TestPostgresMCP(unittest.TestCase):
    def setUp(self):
        # Reset mocks if needed, though patch handles most
        pass

    @patch.object(main_server.psycopg2, "connect")
    def test_list_tables_success(self, mock_connect):
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock data: list of tuples
        mock_cursor.fetchall.return_value = [("users",), ("products",)]

        # Execute
        result = list_tables()

        # Verify
        self.assertIn("users", result)
        self.assertIn("products", result)
        self.assertIn("Tables in database:", result)

        # Verify SQL execution
        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args
        self.assertIn("SELECT table_name", args[0])

        # Verify connection closed
        mock_conn.close.assert_called_once()

    @patch.object(main_server.psycopg2, "connect")
    def test_describe_table_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock data: list of dict-like objects (since we use DictCursor)
        # In the code: row['column_name'], row['data_type'], row['is_nullable']
        mock_cursor.fetchall.return_value = [
            {"column_name": "id", "data_type": "integer", "is_nullable": "NO"},
            {"column_name": "name", "data_type": "varchar", "is_nullable": "YES"}
        ]

        result = describe_table("users")

        self.assertIn("Schema for table 'users'", result)
        self.assertIn("id (integer)", result)
        self.assertIn("name (varchar) [NULLABLE]", result)

        mock_cursor.execute.assert_called_once()

    @patch.object(main_server.psycopg2, "connect")
    def test_describe_table_not_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        result = describe_table("nonexistent")

        self.assertIn("not found", result)

    @patch.object(main_server.psycopg2, "connect")
    def test_execute_read_query_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock description for headers
        mock_cursor.description = [("id",), ("username",)]
        # Mock rows
        mock_cursor.fetchall.return_value = [
            [1, "jdoe"],
            [2, "asmith"]
        ]

        result = execute_read_query("SELECT * FROM users")

        self.assertIn("Query returned 2 rows", result)
        self.assertIn("id | username", result)
        self.assertIn("1 | jdoe", result)

        # Verify session set to readonly
        mock_conn.set_session.assert_called_with(readonly=True)

    def test_execute_read_query_security_check(self):
        # Should not even connect to DB
        result = execute_read_query("DELETE FROM users")
        self.assertIn("Error: Only SELECT queries are allowed", result)

    @patch.object(main_server.psycopg2, "connect")
    def test_execute_read_query_no_results(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        result = execute_read_query("SELECT * FROM empty_table")
        self.assertIn("Query returned no results", result)

    @patch.object(main_server.psycopg2, "connect")
    def test_connection_error(self, mock_connect):
        mock_connect.side_effect = Exception("Connection failed")

        # Suppress logging for this test to keep output clean
        with patch.object(main_server, "logger"):
            with self.assertRaises(RuntimeError):
                list_tables()

if __name__ == "__main__":
    unittest.main()
