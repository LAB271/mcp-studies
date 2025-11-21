# Spike: Logging Strategies for MCP Servers

## Learning Objective
**Primary Question:** How do we implement clean, production-ready logging for MCP servers without interfering with the STDIO transport protocol?

**Context:** MCP servers using STDIO transport communicate through stdin/stdout, which means traditional print-based logging interferes with protocol messages. Additionally, third-party libraries (uvicorn, anyio, MCP SDK) produce verbose logs that clutter development output. We need a logging strategy that provides useful debugging information without breaking the protocol or creating noise.

**Success Criteria:**
- Implement logging that doesn't interfere with STDIO MCP communication
- Suppress or harmonize verbose third-party library logs
- Create clean, readable output for development and production
- Maintain compatibility with MCP protocol requirements
- Demonstrate working examples with HTTP transport (alternative to STDIO)

## Hypothesis
**We believe that:** Using HTTP transport instead of STDIO, combined with proper logging configuration, will allow clean, structured logging without protocol interference.

**Because:** HTTP transport separates data channels (HTTP requests/responses vs. log output), and Python's logging module allows fine-grained control over log levels and formats.

**We'll know we're right when:** We can run an MCP server with clear, informative logs that show only essential information, with all protocol communication working correctly and no spam from third-party libraries.

## Scope & Constraints
- **Time Box:** 3-4 hours for exploration and implementation
- **Out of Scope:**
  - STDIO transport with file-based logging
  - Log aggregation and centralized logging systems
  - Performance optimization of logging
  - Log rotation and management
- **Dependencies:**
  - Understanding of Python logging module
  - MCP SDK with HTTP transport support (SSE/streamable)
  - Prior knowledge from spike 001_demos

## Exploration Log
### 2025-02-11 - Problem Identification
- Identified that STDIO transport prevents traditional logging
- Recognized verbose output from uvicorn, anyio, and MCP SDK internals
- Noted that development debugging is difficult with noisy logs
- Decided to explore HTTP transport as alternative to STDIO

### 2025-02-11 - HTTP Transport Implementation
- Implemented `main_server.py` using HTTP/SSE transport
- Configured custom logging format with timestamps and structure
- Successfully suppressed uvicorn INFO logs using environment variables
- Suppressed anyio and MCP internal logs via logging configuration
- Created clean startup messages with emoji indicators

### 2025-02-11 - Testing and Refinement
- Created test suite in `test_002_logging.py`
- Tested with curl commands and verified JSON responses
- Validated that tool calls generate appropriate logs
- Confirmed clean output format suitable for production
- Documented usage examples and integration patterns

## Key Insights
- **✅ Confirmed:**
  - HTTP transport (SSE/streamable) eliminates STDIO logging conflicts
  - Environment variable `UVICORN_LOG_LEVEL=warning` effectively silences uvicorn INFO logs
  - Python logging configuration can suppress specific library logs (anyio, MCP internals)
  - Custom log formatting provides clean, professional output
  - Emoji indicators improve log readability during development
  - HTTP transport maintains full MCP protocol compatibility

- **❌ Challenged:**
  - STDIO transport cannot be easily combined with stdout logging
  - Default logging configurations are too verbose for development
  - Third-party libraries don't respect global logging levels consistently
  - Need to carefully test each library's logging behavior

- **🤔 Questions Raised:**
  - How do we handle logging for STDIO-based servers in production?
  - What are best practices for structured logging (JSON) in MCP servers?
  - How do we integrate with log aggregation systems?
  - Should we create a logging middleware or decorator pattern?
  - What's the performance impact of detailed logging?

## Recommendation
**Status:** Complete

**Decision:** Integrate HTTP transport with harmonized logging for production servers; use file-based logging for STDIO transport

**Rationale:** The HTTP transport solution provides clean, debuggable logs without protocol interference. For use cases requiring STDIO transport (e.g., Claude Desktop integration), file-based logging should be used instead. The logging configuration patterns established here work well for both development and production.

**Next Steps:**
- Create logging configuration templates for new MCP servers
- Document file-based logging approach for STDIO transport
- Explore structured logging (JSON) for production monitoring
- Consider creating a logging utility module for reuse
- Test logging behavior under high load

## Reference Materials
- **Code Location:** `spikes/002_logging/`
  - `main_mcp_server.py` - Clean MCP server with harmonized logging and HTTP transport
  - `test_002_logging.py` - Test suite with curl command examples
- **Related Spikes:**
  - Spike 001: MCP SDK Demo Implementations (foundational patterns)
- **External Resources:**
  - [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
  - [MCP HTTP Transport](https://modelcontextprotocol.io/)
  - [Uvicorn Logging Configuration](https://www.uvicorn.org/settings/#logging)
  - [SSE (Server-Sent Events) Protocol](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## Usage Examples

### Starting the Server
```bash
# From project root
uv run spikes/002_logging/main_server.py
```

Expected clean output:
```
🚀 Starting Clean MCP Server
📍 Endpoint: http://127.0.0.1:8000/mcp
🔧 Tools: greet, calculate
📄 Resources: server://info
```

### Testing Tools
```bash
# Greet tool
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"greet","arguments":{"name":"Alice"}}}'

# Calculate tool
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"calculate","arguments":{"expression":"15+27"}}}'
```

### Logging Configuration Pattern
```python
# Suppress verbose libraries
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("anyio").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)

# Custom format with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
