import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock mcp and uvicorn modules before importing main_server
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()
sys.modules['uvicorn.config'] = MagicMock()

# Add parent directory to path to import main_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_server import GraphDatabase, mcp_factory

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

    @patch('main_server.GraphDatabase.connect')
    def test_get_session(self, mock_connect):
        self.db.driver = MagicMock()
        self.db.driver.session.return_value = "mock_session"
        
        session = self.db.get_session()
        
        self.assertEqual(session, "mock_session")
        self.db.driver.session.assert_called_with(database="neo4j")

    @patch('main_server.GraphDatabase.get_session')
    def test_query_success(self, mock_get_session):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [{"key": "value"}]
        mock_session.run.return_value = mock_result
        mock_get_session.return_value = mock_session

        result = self.db.query("MATCH (n) RETURN n")
        
        self.assertEqual(result, [{"key": "value"}])
        mock_session.run.assert_called_with("MATCH (n) RETURN n")

    @patch('main_server.GraphDatabase.get_session')
    def test_query_failure(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.run.side_effect = Exception("DB Error")
        mock_get_session.return_value = mock_session

        with self.assertRaises(Exception) as context:
            self.db.query("MATCH (n) RETURN n")
        
        self.assertIn("Database query failed", str(context.exception))

    @patch('main_server.GraphDatabase.query')
    def test_get_all_documents(self, mock_query):
        mock_query.return_value = [{"id": "1", "title": "Doc 1"}]
        
        result = self.db.get_all_documents()
        
        self.assertEqual(result, [{"id": "1", "title": "Doc 1"}])
        mock_query.assert_called_once()
        self.assertIn("MATCH (d:Document)", mock_query.call_args[0][0])

    @patch('main_server.GraphDatabase.query')
    def test_search_chunks(self, mock_query):
        mock_query.return_value = [{"text": "chunk text", "position": 1}]
        
        result = self.db.search_chunks("search term", limit=10)
        
        self.assertEqual(result, [{"text": "chunk text", "position": 1}])
        mock_query.assert_called_once()
        args, kwargs = mock_query.call_args
        self.assertIn("MATCH (c:Chunk)", args[0])
        self.assertEqual(kwargs['text'], "search term")
        self.assertEqual(kwargs['limit'], 10)

    @patch('main_server.GraphDatabase.query')
    def test_get_document_chunks(self, mock_query):
        mock_query.return_value = [{"text": "chunk text", "position": 1}]
        
        result = self.db.get_document_chunks("Doc Title", limit=5)
        
        self.assertEqual(result, [{"text": "chunk text", "position": 1}])
        mock_query.assert_called_once()
        args, kwargs = mock_query.call_args
        self.assertIn("MATCH (d:Document)-[:CONTAINS]->(c:Chunk)", args[0])
        self.assertEqual(kwargs['title'], "Doc Title")
        self.assertEqual(kwargs['limit'], 5)

    @patch('main_server.GraphDatabase.query')
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

    @patch('main_server.GraphDatabase.query')
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

class TestMCPFactory(unittest.TestCase):
    @patch('main_server.FastMCP')
    @patch('main_server.GraphDatabase')
    def test_mcp_factory(self, mock_db, mock_fastmcp):
        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance
        
        mcp = mcp_factory("test_app")
        
        self.assertEqual(mcp, mock_mcp_instance)
        mock_fastmcp.assert_called()
        mock_db.assert_called()

if __name__ == '__main__':
    unittest.main()
