import os
import sys
import unittest
from unittest.mock import patch

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_mcp_server = load_spike_module("000_stdio", "main_mcp_server")
get_test_resource = main_mcp_server.get_test_resource
greet = main_mcp_server.greet
greet_user = main_mcp_server.greet_user
main = main_mcp_server.main
mcp = main_mcp_server.mcp


class TestStdioServer(unittest.TestCase):
    def test_greet(self):
        result = greet("World")
        self.assertEqual(result, "Hello, World!")

    def test_greet_user(self):
        # Test default style
        result = greet_user("Alice")
        self.assertIn("warm, friendly greeting", result)
        self.assertIn("Alice", result)

        # Test formal style
        result = greet_user("Bob", style="formal")
        self.assertIn("formal, professional greeting", result)
        self.assertIn("Bob", result)

        # Test casual style
        result = greet_user("Charlie", style="casual")
        self.assertIn("casual, relaxed greeting", result)
        self.assertIn("Charlie", result)

        # Test unknown style (fallback to friendly)
        result = greet_user("Dave", style="unknown")
        self.assertIn("warm, friendly greeting", result)

    def test_get_test_resource(self):
        result = get_test_resource()
        self.assertEqual(result, "This is a test resource")

    @patch.object(mcp, "run")
    def test_main(self, mock_run):
        main()
        mock_run.assert_called_once_with(transport="stdio")


if __name__ == "__main__":
    unittest.main()
