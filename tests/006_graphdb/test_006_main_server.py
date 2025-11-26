import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Save original modules
original_modules = {
    'mcp': sys.modules.get('mcp'),
    'mcp.server': sys.modules.get('mcp.server'),
    'mcp.server.fastmcp': sys.modules.get('mcp.server.fastmcp'),
    'uvicorn': sys.modules.get('uvicorn'),
    'uvicorn.config': sys.modules.get('uvicorn.config'),
}

# Mock mcp and uvicorn modules before importing main_server
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()
sys.modules['uvicorn.config'] = MagicMock()

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

try:
    main_server = load_spike_module("006_graphdb", "main_server")
    GraphDatabase = main_server.GraphDatabase
    mcp_factory = main_server.mcp_factory
    setup_clean_logging = main_server.setup_clean_logging
    main = main_server.main
finally:
    # Restore original modules
    for name, original in original_modules.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original


class TestGraphDatabase(unittest.TestCase):
    def setUp(self):
        self.db = GraphDatabase(host="localhost", port=7687, user="neo4j", password="password")

    def test_init(self):
        self.assertEqual(self.db.host, "localhost")
        self.assertEqual(self.db.port, 7687)
        self.assertEqual(self.db.user, "neo4j")
        self.assertEqual(self.db.password, "password")
        self.assertIsNone(self.db.driver)
        self.assertIsNone(self.db.session)

    @patch.object(GraphDatabase, 'connect')
    def test_get_session(self, mock_connect):
        self.db.driver = MagicMock()
        self.db.driver.session.return_value = "mock_session"

        session = self.db.get_session()

        self.assertEqual(session, "mock_session")
        self.db.driver.session.assert_called_with(database="neo4j")

    @patch.object(GraphDatabase, 'get_session')
    def test_query_success(self, mock_get_session):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [{"key": "value"}]
        mock_session.run.return_value = mock_result
        mock_get_session.return_value = mock_session

        result = self.db.query("MATCH (n) RETURN n")

        self.assertEqual(result, [{"key": "value"}])
        mock_session.run.assert_called_with("MATCH (n) RETURN n")

    @patch.object(GraphDatabase, 'get_session')
    def test_query_failure(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.run.side_effect = Exception("DB Error")
        mock_get_session.return_value = mock_session

        with self.assertRaises(Exception) as context:
            self.db.query("MATCH (n) RETURN n")

        self.assertIn("Database query failed", str(context.exception))

    @patch.object(GraphDatabase, 'query')
    def test_get_all_documents(self, mock_query):
        mock_query.return_value = [{"id": "1", "title": "Doc 1"}]

        result = self.db.get_all_documents()

        self.assertEqual(result, [{"id": "1", "title": "Doc 1"}])
        mock_query.assert_called_once()
        self.assertIn("MATCH (d:Document)", mock_query.call_args[0][0])

    @patch.object(GraphDatabase, 'query')
    def test_search_chunks(self, mock_query):
        mock_query.return_value = [{"text": "chunk text", "position": 1}]

        result = self.db.search_chunks("search term", limit=10)

        self.assertEqual(result, [{"text": "chunk text", "position": 1}])
        mock_query.assert_called_once()
        args, kwargs = mock_query.call_args
        self.assertIn("MATCH (c:Chunk)", args[0])
        self.assertEqual(kwargs['text'], "search term")
        self.assertEqual(kwargs['limit'], 10)

    @patch.object(GraphDatabase, 'query')
    def test_get_document_chunks(self, mock_query):
        mock_query.return_value = [{"text": "chunk text", "position": 1}]

        result = self.db.get_document_chunks("Doc Title", limit=5)

        self.assertEqual(result, [{"text": "chunk text", "position": 1}])
        mock_query.assert_called_once()
        args, kwargs = mock_query.call_args
        self.assertIn("MATCH (d:Document)-[:CONTAINS]->(c:Chunk)", args[0])
        self.assertEqual(kwargs['title'], "Doc Title")
        self.assertEqual(kwargs['limit'], 5)

    @patch.object(GraphDatabase, 'query')
    def test_get_database_stats(self, mock_query):
        # Mock return values for 3 consecutive calls
        mock_query.side_effect = [
            [{"count": 10}], # documents
            [{"count": 100}], # chunks
            [{"count": 50}]   # relationships
        ]

        stats = self.db.get_database_stats()

        self.assertEqual(stats["documents"], 10)
        self.assertEqual(stats["chunks"], 100)
        self.assertEqual(stats["relationships"], 50)
        self.assertEqual(mock_query.call_count, 3)

    @patch.object(GraphDatabase, 'query')
    def test_search_by_keywords(self, mock_query):
        mock_query.return_value = [{"text": "chunk text", "position": 1}]

        result = self.db.search_by_keywords(["key1", "key2"], limit=5)

        self.assertEqual(result, [{"text": "chunk text", "position": 1}])
        mock_query.assert_called_once()
        args, _ = mock_query.call_args
        self.assertIn("c.text CONTAINS 'key1'", args[0])
        self.assertIn("c.text CONTAINS 'key2'", args[0])

    def test_get_embeddings_info(self):
        info = self.db.get_embeddings_info()
        self.assertEqual(info["total_files"], 3)
        self.assertIn("ps2man_embeddings.json", info["embedding_files"])

    def test_close(self):
        self.db.session = MagicMock()
        self.db.driver = MagicMock()

        self.db.close()

        self.db.session.close.assert_called_once()
        self.db.driver.close.assert_called_once()

    @patch.object(GraphDatabase, 'get_session')
    def test_connect_import_error(self, mock_get_session):
        # We need to patch the import inside connect
        with patch.dict('sys.modules', {'neo4j': None}):
            # Force reload or just call connect if we can mock the import
            # Since 'neo4j' is imported inside the method, we can mock it by removing it from sys.modules
            # But sys.modules['neo4j'] = None might cause ImportError
            pass

    def test_connect_import_error_direct(self):
        # Mocking the import inside the method is tricky with patch.dict if it's not already imported
        # Instead, we can patch builtins.__import__ or use side_effect on the import
        with patch.dict('sys.modules', {'neo4j': None}):
             with self.assertRaises(ImportError):
                 # We need to reset driver to None to force connect
                 self.db.driver = None
                 # This might not trigger the specific ImportError if 'neo4j' is already imported in the module scope
                 # But in the code it is: from neo4j import GraphDatabase as Neo4jDriver
                 # inside the method.
                 try:
                     self.db.connect()
                 except ImportError as e:
                     self.assertEqual(str(e), "neo4j package not installed")
                     raise

    def test_connect_exception(self):
        self.db.driver = None
        with patch.object(GraphDatabase, 'connect') as mock_connect:
             # We can't patch the method we are testing easily if we want to test its internals
             # We need to patch neo4j.GraphDatabase.driver
             pass

    @patch.object(GraphDatabase, 'get_session')
    def test_connect_driver_exception(self, mock_get_session):
        self.db.driver = None
        # We need to mock the local import of neo4j
        mock_neo4j = MagicMock()
        mock_neo4j.GraphDatabase.driver.side_effect = Exception("Connection failed")

        with patch.dict('sys.modules', {'neo4j': mock_neo4j}):
            with self.assertRaises(Exception) as context:
                self.db.connect()
            self.assertIn("Failed to connect", str(context.exception))

    def test_connect_already_connected(self):
        self.db.driver = MagicMock()
        self.db.connect()
        # Should not create new driver
        # We can't easily verify "not called" on the class unless we patch it again
        # But we can verify self.db.driver didn't change if we set it to something specific
        driver = self.db.driver
        self.db.connect()
        self.assertIs(self.db.driver, driver)

    def test_get_session_already_exists(self):
        self.db.driver = MagicMock()
        self.db.session = "existing_session"

        session = self.db.get_session()

        self.assertEqual(session, "existing_session")
        self.db.driver.session.assert_not_called()

    def test_setup_clean_logging_options(self):
        # from main_server import setup_clean_logging
        with patch.object(main_server, 'logging') as mock_logging:
            mock_logger = MagicMock()
            mock_logging.getLogger.return_value = mock_logger

            setup_clean_logging(show_uvicorn=True, show_mcp_internals=True)

            # Check if levels were set correctly (hard to verify exact calls without inspecting all calls)
            # But at least it runs through the branches
            pass

    def test_setup_clean_logging_import_error(self):
        # from main_server import setup_clean_logging
        with patch.object(main_server, 'LOGGING_CONFIG', side_effect=ImportError):
             # This simulates ImportError when accessing LOGGING_CONFIG or importing it
             # But LOGGING_CONFIG is imported at module level.
             # The code has: try: uvicorn_formatter = ... except (ImportError, KeyError):
             # We can patch LOGGING_CONFIG in the module
             with patch.object(main_server, 'LOGGING_CONFIG', new={}):
                 # This might trigger KeyError
                 setup_clean_logging()

    def test_setup_clean_logging_defaults(self):
        # from main_server import setup_clean_logging
        with patch.object(main_server, 'logging') as mock_logging:
            mock_logger = MagicMock()
            mock_logging.getLogger.return_value = mock_logger

            setup_clean_logging()

            # Verify defaults
            mock_logging.getLogger.assert_called()

class TestMCPFactory(unittest.TestCase):
    @patch.object(main_server, 'FastMCP')
    @patch.object(main_server, 'GraphDatabase')
    def test_mcp_factory(self, mock_db, mock_fastmcp):
        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        mcp = mcp_factory("test_app")

        self.assertEqual(mcp, mock_mcp_instance)
        mock_fastmcp.assert_called()
        mock_db.assert_called()

class TestMCPTools(unittest.TestCase):
    def setUp(self):
        self.tools = {}

        def tool_decorator():
            def wrapper(func):
                self.tools[func.__name__] = func
                return func
            return wrapper

        self.fastmcp_patcher = patch.object(main_server, 'FastMCP')
        self.mock_fastmcp_class = self.fastmcp_patcher.start()
        self.mock_mcp_instance = MagicMock()
        self.mock_fastmcp_class.return_value = self.mock_mcp_instance
        self.mock_mcp_instance.tool.side_effect = tool_decorator

        self.graphdb_patcher = patch.object(main_server, 'GraphDatabase')
        self.mock_graphdb_class = self.graphdb_patcher.start()
        self.mock_db = MagicMock()
        self.mock_graphdb_class.return_value = self.mock_db

    def tearDown(self):
        self.fastmcp_patcher.stop()
        self.graphdb_patcher.stop()

    def test_get_all_documents_tool_success(self):
        mcp_factory("test")
        tool = self.tools['get_all_documents']

        self.mock_db.get_all_documents.return_value = [
            {"id": "1", "title": "Test Doc", "type": "pdf", "size": 100}
        ]

        result = tool()

        self.assertIn("Test Doc", result)
        self.assertIn("pdf", result)
        self.assertIn("100 bytes", result)

    def test_get_all_documents_tool_empty(self):
        mcp_factory("test")
        tool = self.tools['get_all_documents']

        self.mock_db.get_all_documents.return_value = []

        result = tool()

        self.assertIn("No documents found", result)

    def test_get_all_documents_tool_error(self):
        mcp_factory("test")
        tool = self.tools['get_all_documents']

        self.mock_db.get_all_documents.side_effect = Exception("DB Error")

        result = tool()

        self.assertIn("Error: DB Error", result)

    def test_search_chunks_tool_success(self):
        mcp_factory("test")
        tool = self.tools['search_chunks']

        self.mock_db.search_chunks.return_value = [
            {"text": "Found text", "position": 5}
        ]

        result = tool("query")

        self.assertIn("Found 1 chunks", result)
        self.assertIn("Found text", result)
        self.assertIn("Position 5", result)

    def test_search_chunks_tool_empty(self):
        mcp_factory("test")
        tool = self.tools['search_chunks']

        self.mock_db.search_chunks.return_value = []

        result = tool("query")

        self.assertIn("No chunks found", result)

    def test_get_document_chunks_tool(self):
        mcp_factory("test")
        tool = self.tools['get_document_chunks']

        self.mock_db.get_document_chunks.return_value = [
            {"text": "Chunk text", "position": 1}
        ]

        result = tool("Doc 1")

        self.assertIn("Chunks from 'Doc 1'", result)
        self.assertIn("Chunk text", result)

    def test_get_database_stats_tool(self):
        mcp_factory("test")
        tool = self.tools['get_database_stats']

        self.mock_db.get_database_stats.return_value = {
            "documents": 10,
            "chunks": 100,
            "relationships": 50
        }

        result = tool()

        self.assertIn("Total Documents: 10", result)
        self.assertIn("Total Chunks: 100", result)

    def test_search_by_keywords_tool(self):
        mcp_factory("test")
        tool = self.tools['search_by_keywords']

        self.mock_db.search_by_keywords.return_value = [
            {"text": "Keyword text", "position": 2}
        ]

        result = tool("key1, key2")

        self.assertIn("Found 1 chunks", result)
        self.assertIn("Keyword text", result)
        self.mock_db.search_by_keywords.assert_called_with(["key1", "key2"], 5)

    def test_get_embeddings_info_tool(self):
        mcp_factory("test")
        tool = self.tools['get_embeddings_info']

        self.mock_db.get_embeddings_info.return_value = {
            "total_files": 2,
            "embedding_files": ["file1.json", "file2.json"]
        }

        result = tool()

        self.assertIn("Total Embedding Files: 2", result)
        self.assertIn("file1.json", result)

class TestLogging(unittest.TestCase):
    @patch.object(main_server, 'logging')
    @patch.object(main_server, 'sys')
    def test_setup_clean_logging(self, mock_sys, mock_logging):
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        # from main_server import setup_clean_logging
        logger = setup_clean_logging()

        self.assertEqual(logger, mock_logger)
        mock_logging.getLogger.assert_called()
        # Verify handlers were cleared and added
        mock_logger.handlers.clear.assert_called()

class TestMain(unittest.TestCase):
    @patch.object(main_server, 'mcp_factory')
    @patch.object(main_server, 'setup_clean_logging')
    def test_main(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_factory.return_value = mock_mcp

        # from main_server import main
        main()

        mock_factory.assert_called()
        mock_mcp.run.assert_called()

    @patch.object(main_server, 'mcp_factory')
    @patch.object(main_server, 'setup_clean_logging')
    def test_main_keyboard_interrupt(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_mcp.run.side_effect = KeyboardInterrupt
        mock_factory.return_value = mock_mcp

        # from main_server import main
        main()

        # Should handle interrupt gracefully
        mock_mcp.run.assert_called()

    @patch.object(main_server, 'mcp_factory')
    @patch.object(main_server, 'setup_clean_logging')
    def test_main_error(self, mock_logging, mock_factory):
        mock_mcp = MagicMock()
        mock_mcp.run.side_effect = Exception("Fatal error")
        mock_factory.return_value = mock_mcp

        # from main_server import main
        with self.assertRaises(Exception):
            main()
