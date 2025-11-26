import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Save original modules
original_modules = {
    "sentence_transformers": sys.modules.get("sentence_transformers"),
    "pdfplumber": sys.modules.get("pdfplumber"),
    "neo4j": sys.modules.get("neo4j"),
}

# Mock dependencies before importing pipeline modules
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["pdfplumber"] = MagicMock()
sys.modules["neo4j"] = MagicMock()

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module  # noqa: E402

try:
    extract_pdfs = load_spike_module("006_graphdb", "pipeline/extract_pdfs")
    extract_pdf_text = extract_pdfs.extract_pdf_text

    generate_embeddings_mod = load_spike_module("006_graphdb", "pipeline/generate_embeddings")
    TextChunker = generate_embeddings_mod.TextChunker
    generate_embeddings = generate_embeddings_mod.generate_embeddings

    load_to_neo4j = load_spike_module("006_graphdb", "pipeline/load_to_neo4j")
    Neo4jLoader = load_to_neo4j.Neo4jLoader
finally:
    # Restore original modules
    for name, original in original_modules.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original


class TestTextChunker(unittest.TestCase):
    def test_chunk_text(self):
        chunker = TextChunker(chunk_size=10, overlap=2)
        text = "one two three four five six seven eight nine ten eleven twelve"
        chunks = chunker.chunk_text(text, "source_doc")

        self.assertTrue(len(chunks) > 0)
        self.assertEqual(chunks[0]["source"], "source_doc")
        self.assertIn("text", chunks[0])
        self.assertIn("position", chunks[0])


class TestExtractPDFs(unittest.TestCase):
    @patch.object(extract_pdfs.pdfplumber, "open")
    def test_extract_pdf_text_success(self, mock_pdf_open):
        # Mock PDF object
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page content"
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Mock file open
        with patch("builtins.open", mock_open()) as mock_file:
            result = extract_pdf_text(Path("test.pdf"), Path("output.txt"))

            self.assertTrue(result)
            mock_file.assert_called_with(Path("output.txt"), "w", encoding="utf-8")
            mock_file().write.assert_called()

    @patch.object(extract_pdfs.pdfplumber, "open")
    def test_extract_pdf_text_failure(self, mock_pdf_open):
        mock_pdf_open.side_effect = Exception("PDF Error")

        result = extract_pdf_text(Path("test.pdf"), Path("output.txt"))

        self.assertFalse(result)

    def test_main_no_dir(self):
        with patch.object(extract_pdfs, "Path") as MockPath:
            # Mock the path chain: Path(__file__).parent.parent / "graph_data" / "documents"
            mock_doc_path = MockPath.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value
            mock_doc_path.exists.return_value = False

            with self.assertRaises(SystemExit):
                extract_pdfs.main()

    def test_main_no_pdfs(self):
        with patch.object(extract_pdfs, "Path") as MockPath:
            mock_doc_path = MockPath.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value
            mock_doc_path.exists.return_value = True
            mock_doc_path.glob.return_value = []

            extract_pdfs.main()

    def test_main_process_pdfs(self):
        with patch.object(extract_pdfs, "Path") as MockPath:
            mock_doc_path = MockPath.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value
            mock_doc_path.exists.return_value = True

            mock_pdf = MagicMock()
            mock_pdf.with_suffix.return_value.exists.return_value = False
            mock_doc_path.glob.return_value = [mock_pdf]

            with patch.object(extract_pdfs, "extract_pdf_text", return_value=True) as mock_extract:
                extract_pdfs.main()
                mock_extract.assert_called()

    def test_main_skip_existing(self):
        with patch.object(extract_pdfs, "Path") as MockPath:
            mock_doc_path = MockPath.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value
            mock_doc_path.exists.return_value = True

            mock_pdf = MagicMock()
            mock_pdf.with_suffix.return_value.exists.return_value = True
            mock_doc_path.glob.return_value = [mock_pdf]

            with patch.object(extract_pdfs, "extract_pdf_text") as mock_extract:
                extract_pdfs.main()
                mock_extract.assert_not_called()


class TestGenerateEmbeddings(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        generate_embeddings_mod.SentenceTransformer = MagicMock(return_value=self.mock_model)
        self.mock_model.encode.return_value = MagicMock(tolist=lambda: [0.1, 0.2])

    def test_generate_embeddings_success(self):
        with patch("builtins.open", mock_open(read_data="some text content")):
            with patch("json.dump") as mock_json:
                # Mock Path.stat().st_size
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 1024
                    generate_embeddings_mod.generate_embeddings(Path("in.txt"), Path("out.json"))
                    mock_json.assert_called()

    def test_main_no_text_files(self):
        with patch("pathlib.Path.glob", return_value=[]):
            with patch("builtins.print") as mock_print:
                generate_embeddings_mod.main()
                found = any("No text files found" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(found)

    def test_main_full_flow(self):
        mock_txt = MagicMock()
        mock_txt.name = "test.txt"
        mock_txt.stem = "test"

        # We need to mock Path objects carefully because main() creates new Path objects
        # But since we are patching glob, we control the files returned

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.glob", return_value=[mock_txt]),
            patch.object(Path, "exists", side_effect=[False, False]),
            patch.object(generate_embeddings_mod, "generate_embeddings") as mock_gen,
        ):
            generate_embeddings_mod.main()
            mock_gen.assert_called()

    def test_main_error_handling(self):
        mock_txt = MagicMock()
        mock_txt.name = "test.txt"

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.glob", return_value=[mock_txt]),
            patch.object(Path, "exists", return_value=False),
            patch.object(generate_embeddings_mod, "generate_embeddings", side_effect=Exception("Fail")),
        ):
            with patch("builtins.print") as mock_print:
                generate_embeddings_mod.main()
                found = any("Error processing" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(found)


class TestNeo4jLoader(unittest.TestCase):
    def setUp(self):
        self.loader = Neo4jLoader("bolt://localhost:7687", "user", "pass")

    @patch.object(load_to_neo4j, "GraphDatabase")
    def test_connect_success(self, mock_driver_class):
        self.loader.driver = MagicMock()
        self.loader.driver.session.return_value.run.return_value = MagicMock()

        result = self.loader.connect()

        self.assertTrue(result)

    @patch.object(load_to_neo4j, "GraphDatabase")
    def test_connect_failure(self, mock_driver_class):
        self.loader.driver = MagicMock()
        self.loader.driver.session.side_effect = Exception("Connection Error")

        result = self.loader.connect()

        self.assertFalse(result)

    def test_create_constraints(self):
        self.loader.session = MagicMock()
        self.loader.create_constraints()
        self.loader.session.run.assert_called()

    def test_create_constraints_error(self):
        self.loader.session = MagicMock()
        self.loader.session.run.side_effect = Exception("Constraint Error")
        self.loader.create_constraints()
        # Should print error but not raise

    def test_load_text_documents(self):
        self.loader.session = MagicMock()

        with patch("pathlib.Path.glob") as mock_glob:
            mock_path = MagicMock()
            mock_path.name = "test.txt"
            mock_path.stem = "test"
            mock_path.suffix = ".txt"

            # glob is called twice (once for .txt, once for .md)
            # We return [mock_path] for the first call and [] for the second
            mock_glob.side_effect = [[mock_path], []]

            with patch("builtins.open", mock_open(read_data="content")):
                count = self.loader.load_text_documents(Path("docs"))

                self.assertEqual(count, 1)
                self.loader.session.run.assert_called()

    def test_load_text_documents_no_files(self):
        with patch("pathlib.Path.glob", return_value=[]):
            count = self.loader.load_text_documents(Path("docs"))
            self.assertEqual(count, 0)

    def test_load_text_documents_error(self):
        self.loader.session = MagicMock()
        with patch("pathlib.Path.glob") as mock_glob:
            mock_path = MagicMock()
            mock_path.name = "test.txt"
            mock_glob.side_effect = [[mock_path], []]

            with patch("builtins.open", side_effect=Exception("File Error")):
                count = self.loader.load_text_documents(Path("docs"))
                self.assertEqual(count, 0)

    def test_load_embeddings_no_files(self):
        with patch("pathlib.Path.glob", return_value=[]):
            count = self.loader.load_embeddings(Path("embeddings"))
            self.assertEqual(count, 0)

    def test_load_embeddings_success(self):
        self.loader.session = MagicMock()
        with patch("pathlib.Path.glob") as mock_glob:
            mock_path = MagicMock()
            mock_path.name = "test_embeddings.json"
            mock_path.stem = "test_embeddings"
            mock_glob.return_value = [mock_path]

            with patch("builtins.open", mock_open(read_data='[{"id": "1", "text": "t", "position": 0}]')):
                count = self.loader.load_embeddings(Path("embeddings"))
                self.assertEqual(count, 1)

    def test_load_embeddings_error(self):
        self.loader.session = MagicMock()
        with patch("pathlib.Path.glob") as mock_glob:
            mock_path = MagicMock()
            mock_path.name = "test_embeddings.json"
            mock_glob.return_value = [mock_path]

            with patch("builtins.open", side_effect=Exception("File Error")):
                count = self.loader.load_embeddings(Path("embeddings"))
                self.assertEqual(count, 0)

    def test_show_statistics(self):
        self.loader.session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"count": 10}
        mock_result.__iter__.return_value = [{"d.title": "T", "d.type": "txt"}]
        self.loader.session.run.return_value = mock_result

        self.loader.show_statistics()
        self.loader.session.run.assert_called()

    def test_show_statistics_error(self):
        self.loader.session = MagicMock()
        self.loader.session.run.side_effect = Exception("DB Error")
        self.loader.show_statistics()
        # Should print error

    def test_close(self):
        self.loader.session = MagicMock()
        self.loader.driver = MagicMock()
        self.loader.close()
        self.loader.session.close.assert_called()
        self.loader.driver.close.assert_called()


class TestLoadToNeo4jMain(unittest.TestCase):
    def test_main(self):
        # We need to patch Neo4jLoader in the load_to_neo4j module
        with patch.object(load_to_neo4j, "Neo4jLoader") as MockLoader:
            mock_loader_instance = MockLoader.return_value
            mock_loader_instance.connect.return_value = True
            mock_loader_instance.load_text_documents.return_value = 5
            mock_loader_instance.load_embeddings.return_value = 10

            # Simulate main execution
            with patch.dict(
                "os.environ",
                {"NEO4J_URI": "bolt://localhost:7687", "NEO4J_USER": "neo4j", "NEO4J_PASSWORD": "password"},
            ):
                load_to_neo4j.main()

            MockLoader.assert_called_once()
            mock_loader_instance.connect.assert_called_once()
            mock_loader_instance.create_constraints.assert_called_once()
            mock_loader_instance.load_text_documents.assert_called_once()
            mock_loader_instance.load_embeddings.assert_called_once()
            mock_loader_instance.show_statistics.assert_called_once()
            mock_loader_instance.close.assert_called_once()

    def test_main_connection_failure(self):
        with patch.object(load_to_neo4j, "Neo4jLoader") as MockLoader:
            mock_loader_instance = MockLoader.return_value
            mock_loader_instance.connect.return_value = False

            with self.assertRaises(SystemExit):
                load_to_neo4j.main()


if __name__ == "__main__":
    unittest.main()
