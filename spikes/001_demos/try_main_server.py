#!/usr/bin/env python3
"""
MCP Server Platform - Try Stream Config Client

Simple MCP client to test the server

Copyright (c) 2025 LAB271
SPDX-License-Identifier: Apache-2.0

Run with:
    $ uv run spikes/001_demos/try_main_server.py
"""

import asyncio

import aiohttp


async def test_mcp_server():
    """Test the MCP server with direct HTTP calls"""

    base_url = "http://127.0.0.1:8000"
    mcp_endpoint = f"{base_url}/mcp"  # This is the key - MCP endpoint is at /mcp

    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Try to initialize with the server
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

            print(f"Testing correct MCP endpoint: {mcp_endpoint}")
            async with session.post(
                mcp_endpoint,
                json=init_request,
                headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            ) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text}")

                if response.status == 200:
                    print("✅ SUCCESS! MCP server is working correctly!")
                    print("The issue was that you need to connect to /mcp endpoint, not the root")

                    # Test listing tools
                    tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

                    print("\nTesting tools/list...")
                    async with session.post(
                        mcp_endpoint,
                        json=tools_request,
                        headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
                    ) as tools_response:
                        print(f"Tools Status: {tools_response.status}")
                        tools_text = await tools_response.text()
                        print(f"Tools Response: {tools_text}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the MCP server is running on http://127.0.0.1:8000")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
