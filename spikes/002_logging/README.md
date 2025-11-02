# Clean MCP Server with Harmonized Logging

This directory contains a clean, production-ready MCP (Model Context Protocol) server with harmonized logging that eliminates noise and shows only essential information.

## Purpose

The **Clean Server** demonstrates:
- ✅ **Minimal, organized logging** - No spam, only essential events
- ✅ **Professional output format** - Clean timestamps and structured messages  
- ✅ **Noise suppression** - Silences verbose uvicorn, anyio, and MCP internal logs
- ✅ **Development-friendly** - Easy to read and debug
- ✅ **Production-ready** - Suitable for real deployments

## What's Different

**Before (messy logging):**
```
[11/02/25 09:23:53] INFO     Starting MCP server on http://127.0.0.1:8000
INFO:     Started server process [83004]
INFO:     Waiting for application startup.
INFO     StreamableHTTP session manager started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
[11/02/25 09:24:30] INFO     Created new transport with session ID: b816b0682db64be29ceae6180a8b9527
INFO:     127.0.0.1:56335 - "POST /mcp HTTP/1.1" 200 OK
INFO:     Processing request of type PingRequest
```

**After (clean logging):**
```
09:25:10 [    INFO] clean_server: 🚀 Starting Clean MCP Server
09:25:10 [    INFO] clean_server: 📍 Endpoint: http://127.0.0.1:8000/mcp
09:25:10 [    INFO] clean_server: 🔧 Tools: greet, calculate
09:25:10 [    INFO] clean_server: 📄 Resources: server://info
09:25:15 [    INFO] clean_server: Greeting World
09:25:18 [    INFO] clean_server: Calculated: 2+2 = 4
```

## How to Start the Server

### Prerequisites
Make sure you're in the project root directory and have dependencies installed:
```bash
cd /path/to/mcp-studies
uv sync  # Install dependencies if not already done
```

### Start the Server
```bash
uv run spikes/002_logging/clean_server.py
```

### Expected Output
When you start the server, you should see:
```
🚀 Starting Clean MCP Server
📍 Endpoint: http://127.0.0.1:8000/mcp
🔧 Tools: greet, calculate
📄 Resources: server://info
```

The server will then start on **http://127.0.0.1:8000** and be ready to accept MCP requests.

## Available Features

### 🔧 **Tools**
- **`greet`** - Greet someone by name (defaults to "World")
- **`calculate`** - Safely calculate simple math expressions

### 📄 **Resources**  
- **`server://info`** - Get server information and status

## Testing the Server

### 1. **List Available Tools**
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1", 
    "method": "tools/list",
    "params": {}
  }'
```

### 2. **Call the Greet Tool**
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call", 
    "params": {
      "name": "greet",
      "arguments": {
        "name": "Alice"
      }
    }
  }'
```

### 3. **Calculate Math Expression**
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "calculate",
      "arguments": {
        "expression": "15 + 27"
      }
    }
  }'
```

### 4. **Get Server Info Resource**
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "4", 
    "method": "resources/read",
    "params": {
      "uri": "server://info"
    }
  }'
```

## What to Expect

### ✅ **Clean Server Logs**
- Startup messages with clear emoji indicators
- Tool execution logs (when tools are called)
- No spam from uvicorn, anyio, or MCP internals
- Timestamps in `HH:MM:SS` format
- Structured log levels

### ✅ **Proper JSON Responses**
All API calls return proper JSON responses following the MCP protocol:
```json
{
  "jsonrpc": "2.0",
  "id": "2", 
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Hello, Alice!"
      }
    ]
  }
}
```

### ✅ **Error Handling**
- Graceful handling of client disconnections
- Clear error messages for invalid requests
- Automatic error recovery

### ✅ **Development Features**
- Easy to see what's happening
- Minimal noise for debugging
- Professional output suitable for production

## Stopping the Server

Press `Ctrl+C` to stop the server gracefully:
```
09:30:22 [    INFO] clean_server: 🛑 Server stopped by user
```

## Integration

This clean server can be used with:
- **Claude Desktop** - Add as MCP server in config
- **Custom MCP clients** - Any client supporting MCP protocol
- **Development tools** - Perfect for testing and development
- **Production deployments** - Ready for real-world use

The clean logging makes it ideal for both development and production environments where you need clear, actionable information without noise.