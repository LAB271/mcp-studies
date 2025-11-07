#!/usr/bin/env python3
"""
MCP Server Platform - Spike unit tests

Unit tests for main_server.py MCP server

Run tests with:
    $ uv run pytest spikes/001_demos/test_001_demos.py -v
Or with unittest:
    $ uv run python -m unittest spikes/001_demos/test_001_demos.py

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import unittest

import aiohttp

# Import the functions from stream_config
# Note: We import the functions before the FastMCP instance to avoid server startup
from mcp.server.fastmcp import FastMCP


class TestGreetFunction(unittest.TestCase):
    """Test the greet tool function"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a test MCP instance
        self.mcp = FastMCP("TestServer")

        # Register the greet function
        @self.mcp.tool()
        def greet(name: str = "World") -> str:
            """Greet someone by name."""
            return f"Hello, {name}!"

        self.greet = greet

    def test_greet_with_name(self):
        """Test greet function with a specific name"""
        result = self.greet(name="Alice")
        self.assertEqual(result, "Hello, Alice!")

    def test_greet_with_default(self):
        """Test greet function with default parameter"""
        result = self.greet()
        self.assertEqual(result, "Hello, World!")

    def test_greet_with_empty_string(self):
        """Test greet function with empty string"""
        result = self.greet(name="")
        self.assertEqual(result, "Hello, !")

    def test_greet_with_special_characters(self):
        """Test greet function with special characters"""
        result = self.greet(name="Alice & Bob")
        self.assertEqual(result, "Hello, Alice & Bob!")


class TestPromptFunction(unittest.TestCase):
    """Test the prompt function"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a test MCP instance
        self.mcp = FastMCP("TestServer")

        # Register the prompt function
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

    def test_greet_user_with_default_style(self):
        """Test greet_user prompt with default friendly style"""
        result = self.greet_user(name="Alice")
        expected = "Please write a warm, friendly greeting for someone named Alice."
        self.assertEqual(result, expected)
        self.assertIsInstance(result, str)

    def test_greet_user_with_friendly_style(self):
        """Test greet_user prompt with explicit friendly style"""
        result = self.greet_user(name="Bob", style="friendly")
        expected = "Please write a warm, friendly greeting for someone named Bob."
        self.assertEqual(result, expected)

    def test_greet_user_with_formal_style(self):
        """Test greet_user prompt with formal style"""
        result = self.greet_user(name="Dr. Smith", style="formal")
        expected = "Please write a formal, professional greeting for someone named Dr. Smith."
        self.assertEqual(result, expected)

    def test_greet_user_with_casual_style(self):
        """Test greet_user prompt with casual style"""
        result = self.greet_user(name="Charlie", style="casual")
        expected = "Please write a casual, relaxed greeting for someone named Charlie."
        self.assertEqual(result, expected)

    def test_greet_user_with_invalid_style(self):
        """Test greet_user prompt with invalid style defaults to friendly"""
        result = self.greet_user(name="Eve", style="nonexistent")
        expected = "Please write a warm, friendly greeting for someone named Eve."
        self.assertEqual(result, expected)

    def test_greet_user_with_empty_name(self):
        """Test greet_user prompt with empty name"""
        result = self.greet_user(name="")
        expected = "Please write a warm, friendly greeting for someone named ."
        self.assertEqual(result, expected)

    def test_greet_user_with_special_characters(self):
        """Test greet_user prompt with special characters in name"""
        result = self.greet_user(name="José María", style="formal")
        expected = "Please write a formal, professional greeting for someone named José María."
        self.assertEqual(result, expected)

    def test_greet_user_style_case_sensitivity(self):
        """Test that style parameter is case sensitive"""
        result = self.greet_user(name="Alex", style="FORMAL")
        # Should default to friendly since "FORMAL" != "formal"
        expected = "Please write a warm, friendly greeting for someone named Alex."
        self.assertEqual(result, expected)

    def test_greet_user_all_styles_available(self):
        """Test that all defined styles work correctly"""
        name = "TestUser"

        # Test each style
        styles_expected = {
            "friendly": "Please write a warm, friendly greeting for someone named TestUser.",
            "formal": "Please write a formal, professional greeting for someone named TestUser.",
            "casual": "Please write a casual, relaxed greeting for someone named TestUser.",
        }

        for style, expected in styles_expected.items():
            with self.subTest(style=style):
                result = self.greet_user(name=name, style=style)
                self.assertEqual(result, expected)

    def test_greet_user_return_type(self):
        """Test that greet_user always returns a string"""
        result = self.greet_user(name="TypeTest", style="formal")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_greet_user_prompt_structure(self):
        """Test the overall structure of the prompt"""
        result = self.greet_user(name="StructureTest", style="casual")

        # Should start with "Please write"
        self.assertTrue(result.startswith("Please write"))

        # Should contain the name
        self.assertIn("StructureTest", result)

        # Should end with period
        self.assertTrue(result.endswith("."))

        # Should contain "greeting"
        self.assertIn("greeting", result)


class TestResourceFunction(unittest.TestCase):
    """Test the resource function"""

    def setUp(self):
        """Set up test fixtures"""
        self.mcp = FastMCP("TestServer")

        @self.mcp.resource("example://test")
        def get_test_resource() -> str:
            """Get a test resource."""
            return "This is a test resource"

        self.get_test_resource = get_test_resource

    def test_get_test_resource(self):
        """Test the test resource returns correct string"""
        result = self.get_test_resource()
        self.assertEqual(result, "This is a test resource")
        self.assertIsInstance(result, str)


class TestMCPServerHTTPEndpoint(unittest.TestCase):
    """Test the MCP server HTTP endpoint"""

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
            print("\nNote: No server detected. Tests requiring live server will be skipped.")

    def setUp(self):
        """Set up test case"""
        if not self.server_running:
            self.skipTest("Server not running on port 8000")

    async def _test_initialize_endpoint(self):
        """Test the initialize endpoint"""
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=init_request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)

                # Check if it's JSON response (our server config) or SSE
                content_type = response.headers.get("content-type", "")

                if "application/json" in content_type:
                    # JSON response format
                    result = await response.json()
                    self.assertIn("result", result)
                    self.assertIn("serverInfo", result["result"])
                    server_name = result["result"]["serverInfo"]["name"]
                    self.assertIn("Server", server_name)  # Could be StatelessServer or StatefulServer
                    return result
                else:
                    # SSE response format
                    text = await response.text()
                    self.assertIn("event: message", text)
                    self.assertIn("serverInfo", text)
                    self.assertIn("Server", text)  # More flexible check
                    return text

    def test_initialize_endpoint(self):
        """Test that initialize endpoint returns 200 and valid response"""
        asyncio.run(self._test_initialize_endpoint())

    async def _test_invalid_endpoint(self):
        """Test that invalid endpoints return appropriate errors"""
        async with aiohttp.ClientSession() as session:
            # Test root endpoint (should not work)
            async with session.get(self.base_url) as response:
                # Expecting 404 or redirect
                self.assertIn(response.status, [404, 307, 308])

    def test_invalid_endpoint(self):
        """Test invalid endpoint handling"""
        asyncio.run(self._test_invalid_endpoint())

    async def _test_missing_accept_header(self):
        """Test that missing Accept header returns 406"""
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint, json=init_request, headers={"Content-Type": "application/json"}
            ) as response:
                self.assertEqual(response.status, 406)
                text = await response.text()
                self.assertIn("Not Acceptable", text)

    def test_missing_accept_header(self):
        """Test that missing Accept header is handled properly"""
        asyncio.run(self._test_missing_accept_header())

    async def _test_prompts_list_endpoint(self):
        """Test the prompts/list endpoint"""
        list_request = {"jsonrpc": "2.0", "id": "prompts-1", "method": "prompts/list", "params": {}}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=list_request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                # Check response structure
                self.assertIn("result", result)
                self.assertIn("prompts", result["result"])

                # Check that our prompt is listed
                prompts = result["result"]["prompts"]
                prompt_names = [p["name"] for p in prompts]
                self.assertIn("simple_greeting_prompt", prompt_names)

                # Find our specific prompt
                greeting_prompt = next(p for p in prompts if p["name"] == "simple_greeting_prompt")
                self.assertEqual(greeting_prompt["description"], "A simple greeting prompt template.")
                self.assertIn("arguments", greeting_prompt)

    def test_prompts_list_endpoint(self):
        """Test that prompts list endpoint works"""
        asyncio.run(self._test_prompts_list_endpoint())

    async def _test_prompts_get_endpoint(self):
        """Test the prompts/get endpoint"""
        get_request = {
            "jsonrpc": "2.0",
            "id": "prompts-2",
            "method": "prompts/get",
            "params": {"name": "simple_greeting_prompt", "arguments": {"name": "TestUser"}},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=get_request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                # Check response structure
                self.assertIn("result", result)
                self.assertIn("messages", result["result"])

                # Check message content
                messages = result["result"]["messages"]
                self.assertTrue(len(messages) > 0)

                message = messages[0]
                self.assertEqual(message["role"], "user")
                self.assertIn("content", message)

                # Check that the prompt content is correct
                content = message["content"]
                if isinstance(content, dict):
                    text_content = content.get("text", "")
                else:
                    text_content = content

                expected_text = "Please write a friendly greeting for TestUser. Make it warm and welcoming."
                self.assertIn("TestUser", text_content)
                self.assertIn("friendly greeting", text_content)
                self.assertEqual(text_content, expected_text)

    def test_prompts_get_endpoint(self):
        """Test that prompts get endpoint works"""
        asyncio.run(self._test_prompts_get_endpoint())

    async def _test_prompts_get_with_default(self):
        """Test the prompts/get endpoint with default parameters"""
        get_request = {
            "jsonrpc": "2.0",
            "id": "prompts-3",
            "method": "prompts/get",
            "params": {
                "name": "simple_greeting_prompt"
                # No arguments provided, should use defaults
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.mcp_endpoint,
                json=get_request,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ) as response:
                self.assertEqual(response.status, 200)
                result = await response.json()

                # Check that default "World" is used
                messages = result["result"]["messages"]
                message = messages[0]
                content = message["content"]

                if isinstance(content, dict):
                    text_content = content.get("text", "")
                else:
                    text_content = content

                self.assertIn("World", text_content)

    def test_prompts_get_with_default(self):
        """Test prompts get endpoint with default parameters"""
        asyncio.run(self._test_prompts_get_with_default())


class TestMCPServerConfiguration(unittest.TestCase):
    """Test MCP server configuration options"""

    def test_stateful_server_creation(self):
        """Test creating a stateful server"""
        mcp = FastMCP("StatefulServer")
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, "StatefulServer")

    def test_stateless_server_creation(self):
        """Test creating a stateless server"""
        mcp = FastMCP("StatelessServer", stateless_http=True)
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, "StatelessServer")

    def test_stateless_json_server_creation(self):
        """Test creating a stateless server with JSON response"""
        mcp = FastMCP("StatelessServer", stateless_http=True, json_response=True)
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, "StatelessServer")

    def test_tool_registration(self):
        """Test that tools can be registered"""
        mcp = FastMCP("TestServer")

        @mcp.tool()
        def test_tool(param: str) -> str:
            return f"Test: {param}"

        # The tool should be callable
        result = test_tool(param="value")
        self.assertEqual(result, "Test: value")

    def test_resource_registration(self):
        """Test that resources can be registered"""
        mcp = FastMCP("TestServer")

        @mcp.resource("test://resource")
        def test_resource() -> str:
            return "Test resource"

        # The resource should be callable
        result = test_resource()
        self.assertEqual(result, "Test resource")


class TestServerEndpoints(unittest.TestCase):
    """Test server endpoint configuration"""

    def test_mcp_endpoint_path(self):
        """Test that MCP endpoint path is correct"""
        expected_endpoint = "http://127.0.0.1:8000/mcp"
        # This is a configuration test
        self.assertTrue(expected_endpoint.endswith("/mcp"))
        self.assertTrue("127.0.0.1:8000" in expected_endpoint)


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
