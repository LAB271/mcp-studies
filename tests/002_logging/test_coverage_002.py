import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_mcp_server = load_spike_module("002_logging", "main_mcp_server")
main_server = load_spike_module("002_logging", "main_server")
main = main_server.main
mcp_factory = main_server.mcp_factory
setup_clean_logging = main_server.setup_clean_logging


class TestSpike002(unittest.TestCase):
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

        self.fastmcp_patcher = patch.object(main_server, "FastMCP")
        self.mock_fastmcp_class = self.fastmcp_patcher.start()
        self.mock_mcp_instance = MagicMock()
        self.mock_fastmcp_class.return_value = self.mock_mcp_instance
        self.mock_mcp_instance.tool.side_effect = tool_decorator
        self.mock_mcp_instance.prompt.side_effect = prompt_decorator
        self.mock_mcp_instance.resource.side_effect = resource_decorator

    def tearDown(self):
        self.fastmcp_patcher.stop()

    def test_mcp_factory_tools(self):
        mcp_factory("test_app")

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

        greet_user = self.prompts["greet_user"]
        self.assertIn("friendly", greet_user("Alice"))
        self.assertIn("formal", greet_user("Alice", style="formal"))

    def test_mcp_factory_resources(self):
        mcp_factory("test_app")

        get_server_info = self.resources["server://info"]
        self.assertIn("Clean MCP Server", get_server_info())

    @patch.object(main_server, "logging")
    def test_setup_clean_logging(self, mock_logging):
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        logger = setup_clean_logging()
        self.assertEqual(logger, mock_logger)

        # Test with options
        setup_clean_logging(show_uvicorn=True, show_mcp_internals=True)

    def test_setup_clean_logging_success(self):
        # Mock LOGGING_CONFIG to be valid
        valid_config = {"formatters": {"default": {"fmt": "%(message)s", "datefmt": "%H:%M:%S"}}}
        with patch.object(main_server, "LOGGING_CONFIG", valid_config):
            logger = setup_clean_logging("DEBUG", "test_app")
            self.assertIsNotNone(logger)

    def test_setup_clean_logging_fallback(self):
        # Mock LOGGING_CONFIG to be an empty dict, so accessing keys raises KeyError
        with patch.object(main_server, "LOGGING_CONFIG", {}):
            logger = setup_clean_logging("DEBUG", "test_app")
            # Verify that we got a logger despite the error
            self.assertIsNotNone(logger)

    def test_main_keyboard_interrupt(self):
        self.mock_mcp_instance.run.side_effect = KeyboardInterrupt

        # Should not raise exception
        main("test_app")

        # Verify run was called
        self.mock_mcp_instance.run.assert_called_once()

    def test_main_generic_exception(self):
        self.mock_mcp_instance.run.side_effect = Exception("Generic error")

        with self.assertRaises(Exception):  # noqa: B017
            main("test_app")

    def test_main_closed_resource_error(self):
        self.mock_mcp_instance.run.side_effect = Exception("ClosedResourceError occurred")

        # Should not raise exception
        main("test_app")


class TestMainMcpServer(unittest.TestCase):
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

    def test_mcp_factory_tools(self):
        main_mcp_server.mcp_factory("test_app")

        # Test greet
        greet = self.tools["greet"]
        self.assertEqual(greet("Alice"), "Hello, Alice!")

        # Test calculate
        calculate = self.tools["calculate"]
        self.assertEqual(calculate("1 + 1"), "1 + 1 = 2")
        self.assertIn("Error", calculate("1 + a"))
        self.assertIn("Error", calculate("1 / 0"))

    def test_mcp_factory_prompts(self):
        main_mcp_server.mcp_factory("test_app")

        greet_user = self.prompts["greet_user"]
        self.assertIn("friendly", greet_user("Alice"))
        self.assertIn("formal", greet_user("Alice", style="formal"))

    def test_mcp_factory_resources(self):
        main_mcp_server.mcp_factory("test_app")

        get_server_info = self.resources["server://info"]
        self.assertIn("Clean MCP Server", get_server_info())

    def test_setup_clean_logging_success(self):
        # Mock LOGGING_CONFIG to be valid
        valid_config = {"formatters": {"default": {"fmt": "%(message)s", "datefmt": "%H:%M:%S"}}}
        with patch.object(main_mcp_server, "LOGGING_CONFIG", valid_config):
            logger = main_mcp_server.setup_clean_logging("DEBUG", "test_app")
            self.assertIsNotNone(logger)

    def test_setup_clean_logging_fallback(self):
        # Mock LOGGING_CONFIG to be an empty dict, so accessing keys raises KeyError
        with patch.object(main_mcp_server, "LOGGING_CONFIG", {}):
            logger = main_mcp_server.setup_clean_logging("DEBUG", "test_app")
            self.assertIsNotNone(logger)

    def test_main_keyboard_interrupt(self):
        self.mock_mcp_instance.run.side_effect = KeyboardInterrupt

        # Should not raise exception
        main_mcp_server.main("test_app")

        # Verify run was called
        self.mock_mcp_instance.run.assert_called_once()

    def test_main_generic_exception(self):
        self.mock_mcp_instance.run.side_effect = Exception("Generic error")

        with self.assertRaises(Exception):  # noqa: B017
            main_mcp_server.main("test_app")

    def test_main_closed_resource_error(self):
        self.mock_mcp_instance.run.side_effect = Exception("ClosedResourceError occurred")

        # Should not raise exception
        main_mcp_server.main("test_app")


if __name__ == "__main__":
    unittest.main()
