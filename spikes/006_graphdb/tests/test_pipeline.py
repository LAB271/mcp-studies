import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
from pathlib import Path

# Mock dependencies before importing pipeline modules
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['pdfplumber'] = MagicMock()
sys.modules['neo4j'] = MagicMock()

# Add parent directory to path to import pipeline modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.generate_embeddings import TextChunker, generate_embeddings
from pipeline.extract_pdfs import extract_pdf_text
from pipeline.load_to_neo4j import Neo4jLoader

class TestTextChunker(unittest.TestCase):
    def test_chunk_text(self):
        chunker = TextChunker(chunk_size=10, overlap=2)
        text = "one two three four five six seven eight nine ten eleven twelve"
        chunks = chunker.chunk_text(text, "source_doc")
        
        self.assertTrue(len(chunks) > 0)
        self.assertEqual(chunks[0]['source'], "source_doc")
        self.assertIn('text', chunks[0])
        self.assertIn('position', chunks[0])

class TestExtractPDFs(unittest.TestCase):
    @patch('pipeline.extract_pdfs.pdfplumber.open')
    def test_extract_pdf_text_success(self, mock_pdf_open):
        # Mock PDF object
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page content"
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        # Mock file open
        with patch('builtins.open', mock_open()) as mock_file:
            result = extract_pdf_text(Path("test.pdf"), Path("output.txt"))
            
            self.assertTrue(result)
            mock_file.assert_called_with(Path("output.txt"), 'w', encoding='utf-8')
            mock_file().write.assert_called()

    @patch('pipeline.extract_pdfs.pdfplumber.open')
    def test_extract_pdf_text_failure(self, mock_pdf_open):
        mock_pdf_open.side_effect = Exception("PDF Error")
        
        result = extract_pdf_text(Path("test.pdf"), Path("output.txt"))
        
        self.assertFalse(result)

class TestGenerateEmbeddings(unittest.TestCase):
    @patch('pipeline.generate_embeddings.SentenceTransformer')
    @patch('pathlib.Path.stat')
    def test_generate_embeddings(self, mock_stat, mock_transformer):
        # Mock model
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(tolist=lambda: [0.1, 0.2, 0.3])
        mock_transformer.return_value = mock_model
        
        # Mock stat
        mock_stat.return_value.st_size = 1024
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data="some text content")):
            # Mock json dump
            with patch('json.dump') as mock_json_dump:
                result = generate_embeddings(Path("input.txt"), Path("output.json"))
                
                self.assertTrue(len(result) > 0)
                mock_model.encode.assert_called()
                mock_json_dump.assert_called()

class TestNeo4jLoader(unittest.TestCase):
    def setUp(self):
        self.loader = Neo4jLoader("bolt://localhost:7687", "user", "pass")

    @patch('pipeline.load_to_neo4j.GraphDatabase')
    def test_connect_success(self, mock_driver_class):
        self.loader.driver = MagicMock()
        self.loader.driver.session.return_value.run.return_value = MagicMock()
        
        result = self.loader.connect()
        
        self.assertTrue(result)

    @patch('pipeline.load_to_neo4j.GraphDatabase')
    def test_connect_failure(self, mock_driver_class):
        self.loader.driver = MagicMock()
        self.loader.driver.session.side_effect = Exception("Connection Error")
        
        result = self.loader.connect()
        
        self.assertFalse(result)

    def test_create_constraints(self):
        self.loader.session = MagicMock()
        self.loader.create_constraints()
        self.loader.session.run.assert_called()

    def test_load_text_documents(self):
        self.loader.session = MagicMock()
        
        with patch('pathlib.Path.glob') as mock_glob:
            mock_path = MagicMock()
            mock_path.name = "test.txt"
            mock_path.stem = "test"
            mock_path.suffix = ".txt"
            
            # glob is called twice (once for .txt, once for .md)
            # We return [mock_path] for the first call and [] for the second
            mock_glob.side_effect = [[mock_path], []]
            
            with patch('builtins.open', mock_open(read_data="content")):
                count = self.loader.load_text_documents(Path("docs"))
                
                self.assertEqual(count, 1)
                self.loader.session.run.assert_called()

if __name__ == '__main__':
    unittest.main()
