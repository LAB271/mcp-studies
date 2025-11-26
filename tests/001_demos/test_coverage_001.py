import os
import sys
import unittest
from unittest.mock import patch

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_mcp_server = load_spike_module("001_demos", "main_mcp_server")
main_server = load_spike_module("001_demos", "main_server")


class TestSpike001(unittest.TestCase):
    def test_main_server_greet(self):
        self.assertEqual(main_server.greet("Alice"), "Hello, Alice!")

    def test_main_server_greet_user(self):
        self.assertIn("friendly", main_server.greet_user("Alice"))
        self.assertIn("formal", main_server.greet_user("Alice", style="formal"))
        self.assertIn("casual", main_server.greet_user("Alice", style="casual"))
        self.assertIn("friendly", main_server.greet_user("Alice", style="unknown"))

    def test_main_server_resource(self):
        self.assertEqual(main_server.get_test_resource(), "This is a test resource")

    @patch.object(main_server, "mcp")
    def test_main_server_main(self, mock_mcp):
        main_server.main()
        mock_mcp.run.assert_called_with(transport="streamable-http")

    def test_main_mcp_server_greet(self):
        self.assertEqual(main_mcp_server.greet("Alice"), "Hello, Alice!")

    def test_main_mcp_server_greet_user(self):
        self.assertIn("friendly", main_mcp_server.greet_user("Alice"))

    def test_main_mcp_server_resource(self):
        self.assertEqual(main_mcp_server.get_test_resource(), "This is a test resource")

    @patch.object(main_mcp_server, "mcp")
    def test_main_mcp_server_main(self, mock_mcp):
        main_mcp_server.main()
        mock_mcp.run.assert_called_with(transport="streamable-http")


if __name__ == "__main__":
    unittest.main()
