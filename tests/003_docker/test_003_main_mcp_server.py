import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_mcp_server = load_spike_module("003_docker", "main_mcp_server")
main = main_mcp_server.main
mcp_factory = main_mcp_server.mcp_factory
setup_clean_logging = main_mcp_server.setup_clean_logging


class TestDockerMCPServer(unittest.TestCase):
    def setUp(self):
        self.tools = {}
        self.prompts = {}
        self.resources = {}

        def tool_decorator():
            def wrapper(func):
                self.tools[func.__name__] = func
                return func

            return wrapper

        def prompt_decorator():
            def wrapper(func):
                self.prompts[func.__name__] = func
                return func

            return wrapper

        def resource_decorator(uri):
            def wrapper(func):
                self.resources[uri] = func
                return func

            return wrapper

        self.fastmcp_patcher = patch.object(main_mcp_server, "FastMCP")
        self.mock_fastmcp_class = self.fastmcp_patcher.start()
        self.mock_mcp_instance = MagicMock()
        self.mock_fastmcp_class.return_value = self.mock_mcp_instance
        self.mock_mcp_instance.tool.side_effect = tool_decorator
        self.mock_mcp_instance.prompt.side_effect = prompt_decorator
        self.mock_mcp_instance.resource.side_effect = resource_decorator

    def tearDown(self):
        self.fastmcp_patcher.stop()

    def test_mcp_factory(self):
        mcp = mcp_factory("test_app")
        self.assertEqual(mcp, self.mock_mcp_instance)

        # Test tools
        self.assertIn("greet", self.tools)
        self.assertIn("calculate", self.tools)

        # Test greet
        greet = self.tools["greet"]
        self.assertEqual(greet("Alice"), "Hello, Alice!")

        # Test calculate
        calculate = self.tools["calculate"]
        self.assertEqual(calculate("1 + 1"), "1 + 1 = 2")
        self.assertIn("Error", calculate("1 + a"))
        self.assertIn("Error", calculate("1 / 0"))

    def test_mcp_factory_prompts(self):
        mcp_factory("test_app")
        if "greet_user" in self.prompts:
            greet_user = self.prompts["greet_user"]
            self.assertIn("friendly", greet_user("Alice"))
            self.assertIn("formal", greet_user("Alice", style="formal"))

    def test_mcp_factory_resources(self):
        mcp_factory("test_app")
        if "server://info" in self.resources:
            get_info = self.resources["server://info"]
            self.assertIn("Clean MCP Server", get_info())

    @patch.object(main_mcp_server, "logging")
    def test_setup_clean_logging(self, mock_logging):
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        logger = setup_clean_logging()
        self.assertEqual(logger, mock_logger)

    def test_setup_clean_logging_fallback(self):
        # Mock LOGGING_CONFIG to be an empty dict
        with patch.object(main_mcp_server, "LOGGING_CONFIG", {}):
            logger = setup_clean_logging("DEBUG", "test_app")
            self.assertIsNotNone(logger)

    def test_setup_clean_logging_success(self):
        # Mock LOGGING_CONFIG to be valid
        valid_config = {"formatters": {"default": {"fmt": "%(message)s", "datefmt": "%H:%M:%S"}}}
        with patch.object(main_mcp_server, "LOGGING_CONFIG", valid_config):
            logger = setup_clean_logging("DEBUG", "test_app")
            self.assertIsNotNone(logger)

    def test_main_keyboard_interrupt(self):
        self.mock_mcp_instance.run.side_effect = KeyboardInterrupt
        main("test_app")
        self.mock_mcp_instance.run.assert_called()

    def test_main_generic_exception(self):
        self.mock_mcp_instance.run.side_effect = Exception("Generic error")
        with self.assertRaises(Exception):  # noqa: B017
            main("test_app")

    def test_main_closed_resource_error(self):
        self.mock_mcp_instance.run.side_effect = Exception("ClosedResourceError occurred")
        main("test_app")


if __name__ == "__main__":
    unittest.main()
