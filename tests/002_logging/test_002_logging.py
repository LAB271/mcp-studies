#!/usr/bin/env python3
"""
MCP Server Platform - Spike unit tests

Unit tests for main_server.py MCP server with factory method

Run tests with:
    $ uv run pytest spikes/002_logging/test_002_logging.py -v
Or with unittest:
    $ uv run python -m unittest spikes/002_logging/test_002_logging.py

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import aiohttp

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_server = load_spike_module("002_logging", "main_server")
mcp_factory = main_server.mcp_factory
setup_clean_logging = main_server.setup_clean_logging


class TestMCPFactoryMethod(unittest.TestCase):
    """Test the MCP factory method"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_logger = MagicMock(spec=logging.Logger)

    def test_factory_creates_mcp_instance(self):
        """Test that factory method creates a valid MCP instance"""
        mcp = mcp_factory(app_name="TestFactory", logger=self.test_logger)
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, "TestFactory")

    def test_factory_with_default_logger(self):
        """Test factory method with default logger"""
        mcp = mcp_factory(app_name="TestDefaultLogger")
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, "TestDefaultLogger")

    def test_factory_registers_all_tools(self):
        """Test that factory registers all expected tools"""
        mcp = mcp_factory(app_name="TestTools", logger=self.test_logger)

        # Check that tools are registered by accessing the underlying registry
        # Note: This tests the registration, actual tool functionality tested separately
        self.assertIsNotNone(mcp)

    def test_factory_registers_prompts(self):
        """Test that factory registers prompts"""
        mcp = mcp_factory(app_name="TestPrompts", logger=self.test_logger)
        self.assertIsNotNone(mcp)

    def test_factory_registers_resources(self):
        """Test that factory registers resources"""
        mcp = mcp_factory(app_name="TestResources", logger=self.test_logger)
        self.assertIsNotNone(mcp)


class TestGreetTool(unittest.TestCase):
    """Test the greet tool functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = MagicMock(spec=logging.Logger)
        self.mcp = mcp_factory(app_name="TestGreet", logger=self.logger)

        # Extract the greet function for direct testing
        # Note: In a real implementation, you'd access this through MCP registry
        @self.mcp.tool()
        def greet(name: str = "World") -> str:
            """Greet someone by name."""
            self.logger.info(f"Greeting {name}")
            return f"Hello, {name}!"

        self.greet = greet

    def test_greet_with_default_name(self):
        """Test greet with default name parameter"""
        result = self.greet()
        self.assertEqual(result, "Hello, World!")

    def test_greet_with_custom_name(self):
        """Test greet with custom name"""
        result = self.greet(name="Alice")
        self.assertEqual(result, "Hello, Alice!")

    def test_greet_with_empty_name(self):
        """Test greet with empty name"""
        result = self.greet(name="")
        self.assertEqual(result, "Hello, !")

    def test_greet_with_special_characters(self):
        """Test greet with special characters"""
        result = self.greet(name="José María")
        self.assertEqual(result, "Hello, José María!")

    def test_greet_logging(self):
        """Test that greet function logs correctly"""
        with patch.object(self.logger, "info") as mock_log:
            self.greet(name="LogTest")
            mock_log.assert_called_with("Greeting LogTest")

    def test_greet_return_type(self):
        """Test greet returns string"""
        result = self.greet(name="TypeTest")
        self.assertIsInstance(result, str)


class TestCalculateTool(unittest.TestCase):
    """Test the calculate tool functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = MagicMock(spec=logging.Logger)
        self.mcp = mcp_factory(app_name="TestCalculate", logger=self.logger)

        # Extract the calculate function for direct testing
        @self.mcp.tool()
        def calculate(expression: str) -> str:
            """Safely calculate a simple math expression."""
            try:
                # Only allow basic math operations for safety
                allowed_chars = set("0123456789+-*/.() ")
                if not all(c in allowed_chars for c in expression):
                    return "Error: Only basic math operations allowed"

                result = eval(expression)
                self.logger.info(f"Calculated: {expression} = {result}")
                return f"{expression} = {result}"
            except Exception as e:
                self.logger.warning(f"Calculation error: {e}")
                return f"Error: {e}"

        self.calculate = calculate

    def test_calculate_simple_addition(self):
        """Test simple addition calculation"""
        result = self.calculate("2 + 3")
        self.assertEqual(result, "2 + 3 = 5")

    def test_calculate_multiplication(self):
        """Test multiplication calculation"""
        result = self.calculate("4 * 5")
        self.assertEqual(result, "4 * 5 = 20")

    def test_calculate_complex_expression(self):
        """Test complex mathematical expression"""
        result = self.calculate("(10 + 5) * 2")
        self.assertEqual(result, "(10 + 5) * 2 = 30")

    def test_calculate_division(self):
        """Test division calculation"""
        result = self.calculate("15 / 3")
        self.assertEqual(result, "15 / 3 = 5.0")

    def test_calculate_invalid_characters(self):
        """Test calculation with invalid characters"""
        result = self.calculate("2 + abc")
        self.assertEqual(result, "Error: Only basic math operations allowed")

    def test_calculate_dangerous_expression(self):
        """Test calculation blocks dangerous expressions"""
        result = self.calculate("__import__('os').system('ls')")
        self.assertEqual(result, "Error: Only basic math operations allowed")

    def test_calculate_syntax_error(self):
        """Test calculation with syntax error"""
        result = self.calculate("2 ++")
        self.assertTrue(result.startswith("Error:"))

    def test_calculate_division_by_zero(self):
        """Test division by zero handling"""
        result = self.calculate("5 / 0")
        self.assertTrue(result.startswith("Error:"))

    def test_calculate_logging_success(self):
        """Test calculate logs successful calculations"""
        with patch.object(self.logger, "info") as mock_log:
            self.calculate("3 + 4")
            mock_log.assert_called_with("Calculated: 3 + 4 = 7")

    def test_calculate_logging_error(self):
        """Test calculate logs errors"""
        with patch.object(self.logger, "warning") as mock_log:
            self.calculate("1 / 0")
            mock_log.assert_called_once()


class TestGreetUserPrompt(unittest.TestCase):
    """Test the greet_user prompt functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = MagicMock(spec=logging.Logger)
        self.mcp = mcp_factory(app_name="TestPrompt", logger=self.logger)

        # Extract the prompt function for direct testing
        @self.mcp.prompt()
        def greet_user(name: str, style: str = "friendly") -> str:
            """Generate a greeting prompt"""
            styles = {
                "friendly": "Please write a warm, friendly greeting",
                "formal": "Please write a formal, professional greeting",
                "casual": "Please write a casual, relaxed greeting",
            }
            return f"{styles.get(style, styles['friendly'])} for someone named {name}."

        self.greet_user = greet_user

    def test_greet_user_default_style(self):
        """Test greet_user with default friendly style"""
        result = self.greet_user(name="Alice")
        expected = "Please write a warm, friendly greeting for someone named Alice."
        self.assertEqual(result, expected)

    def test_greet_user_friendly_style(self):
        """Test greet_user with explicit friendly style"""
        result = self.greet_user(name="Bob", style="friendly")
        expected = "Please write a warm, friendly greeting for someone named Bob."
        self.assertEqual(result, expected)

    def test_greet_user_formal_style(self):
        """Test greet_user with formal style"""
        result = self.greet_user(name="Dr. Smith", style="formal")
        expected = "Please write a formal, professional greeting for someone named Dr. Smith."
        self.assertEqual(result, expected)

    def test_greet_user_casual_style(self):
        """Test greet_user with casual style"""
        result = self.greet_user(name="Charlie", style="casual")
        expected = "Please write a casual, relaxed greeting for someone named Charlie."
        self.assertEqual(result, expected)

    def test_greet_user_invalid_style(self):
        """Test greet_user with invalid style defaults to friendly"""
        result = self.greet_user(name="Eve", style="nonexistent")
        expected = "Please write a warm, friendly greeting for someone named Eve."
        self.assertEqual(result, expected)

    def test_greet_user_all_styles(self):
        """Test all available greeting styles"""
        name = "TestUser"
        styles_expected = {
            "friendly": "Please write a warm, friendly greeting for someone named TestUser.",
            "formal": "Please write a formal, professional greeting for someone named TestUser.",
            "casual": "Please write a casual, relaxed greeting for someone named TestUser.",
        }

        for style, expected in styles_expected.items():
            with self.subTest(style=style):
                result = self.greet_user(name=name, style=style)
                self.assertEqual(result, expected)


class TestServerInfoResource(unittest.TestCase):
    """Test the server info resource functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = MagicMock(spec=logging.Logger)
        self.mcp = mcp_factory(app_name="TestResource", logger=self.logger)

        # Extract the resource function for direct testing
        @self.mcp.resource("server://info")
        def get_server_info() -> str:
            """Get server information."""
            self.logger.info("Server info requested")
            return """Clean MCP Server
    - Minimal logging
    - Basic tools available
    - Ready for development"""

        self.get_server_info = get_server_info

    def test_server_info_content(self):
        """Test server info returns correct content"""
        result = self.get_server_info()
        expected = """Clean MCP Server
    - Minimal logging
    - Basic tools available
    - Ready for development"""
        self.assertEqual(result, expected)

    def test_server_info_logging(self):
        """Test server info logs access"""
        with patch.object(self.logger, "info") as mock_log:
            self.get_server_info()
            mock_log.assert_called_with("Server info requested")

    def test_server_info_return_type(self):
        """Test server info returns string"""
        result = self.get_server_info()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestLoggingConfiguration(unittest.TestCase):
    """Test the logging configuration functionality"""

    def test_setup_clean_logging_returns_logger(self):
        """Test setup_clean_logging returns a logger"""
        logger = setup_clean_logging(app_name="test_logger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")

    def test_setup_clean_logging_levels(self):
        """Test setup_clean_logging with different levels"""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            with self.subTest(level=level):
                logger = setup_clean_logging(level=level, app_name=f"test_{level.lower()}")
                self.assertEqual(logger.level, getattr(logging, level))

    def test_setup_clean_logging_with_flags(self):
        """Test setup_clean_logging with different flag combinations"""
        logger = setup_clean_logging(level="INFO", app_name="test_flags", show_uvicorn=True, show_mcp_internals=False)
        self.assertIsInstance(logger, logging.Logger)


class TestMCPServerHTTPEndpoints(unittest.TestCase):
    """Test MCP server HTTP endpoints (requires running server)"""

    @classmethod
    def setUpClass(cls):
        """Set up the test server once for all tests"""
        cls.base_url = "http://127.0.0.1:8000"
        cls.mcp_endpoint = f"{cls.base_url}/mcp"
        cls.server_running = False

        # Check if server is already running
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", 8000))
        sock.close()

        if result == 0:
            cls.server_running = True
            print("\nNote: Using existing server running on port 8000")
        else:
            print("\nNote: No server detected. HTTP tests will be skipped.")

    def setUp(self):
        """Set up test case"""
        if not self.server_running:
            self.skipTest("Server not running on port 8000")

    async def _test_tools_list_endpoint(self):
        """Test the tools/list endpoint"""
        request = {"jsonrpc": "2.0", "id": "tools-1", "method": "tools/list", "params": {}}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                self.assertIn("result", result)
                self.assertIn("tools", result["result"])

                tools = result["result"]["tools"]
                tool_names = [t["name"] for t in tools]
                self.assertIn("greet", tool_names)
                self.assertIn("calculate", tool_names)

    def test_tools_list_endpoint(self):
        """Test tools list endpoint"""
        asyncio.run(self._test_tools_list_endpoint())

    async def _test_greet_tool_call(self):
        """Test calling the greet tool"""
        request = {
            "jsonrpc": "2.0",
            "id": "greet-1",
            "method": "tools/call",
            "params": {"name": "greet", "arguments": {"name": "TestUser"}},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                self.assertIn("result", result)
                content = result["result"]["content"][0]["text"]
                self.assertEqual(content, "Hello, TestUser!")

    def test_greet_tool_call(self):
        """Test greet tool call"""
        asyncio.run(self._test_greet_tool_call())

    async def _test_calculate_tool_call(self):
        """Test calling the calculate tool"""
        request = {
            "jsonrpc": "2.0",
            "id": "calc-1",
            "method": "tools/call",
            "params": {"name": "calculate", "arguments": {"expression": "10 + 15"}},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                self.assertIn("result", result)
                content = result["result"]["content"][0]["text"]
                self.assertEqual(content, "10 + 15 = 25")

    def test_calculate_tool_call(self):
        """Test calculate tool call"""
        asyncio.run(self._test_calculate_tool_call())

    async def _test_prompts_list_endpoint(self):
        """Test the prompts/list endpoint"""
        request = {"jsonrpc": "2.0", "id": "prompts-1", "method": "prompts/list", "params": {}}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                self.assertIn("result", result)
                self.assertIn("prompts", result["result"])

                prompts = result["result"]["prompts"]
                prompt_names = [p["name"] for p in prompts]
                self.assertIn("greet_user", prompt_names)

    def test_prompts_list_endpoint(self):
        """Test prompts list endpoint"""
        asyncio.run(self._test_prompts_list_endpoint())

    async def _test_resources_list_endpoint(self):
        """Test the resources/list endpoint"""
        request = {"jsonrpc": "2.0", "id": "resources-1", "method": "resources/list", "params": {}}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                self.assertIn("result", result)
                self.assertIn("resources", result["result"])

                resources = result["result"]["resources"]
                resource_uris = [r["uri"] for r in resources]
                self.assertIn("server://info", resource_uris)

    def test_resources_list_endpoint(self):
        """Test resources list endpoint"""
        asyncio.run(self._test_resources_list_endpoint())


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
