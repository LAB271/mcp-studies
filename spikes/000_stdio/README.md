# Spike: Stdio MCP Server Foundation

## Learning Objective
**Primary Question:** How do we create a minimal MCP server using stdio transport that demonstrates the core building blocks (tools, prompts, and resources)?

**Context:** Before exploring advanced features like HTTP transport, Docker deployment, or structured data management, we need to understand the fundamental MCP server architecture. The stdio transport provides the simplest way to communicate with an MCP server, making it ideal for learning, testing, and IDE integration (like Cline).

**Success Criteria:** 
- Successfully create and run a FastMCP server with stdio transport
- Implement at least one example of each core MCP primitive: tool, prompt, and resource
- Demonstrate bidirectional communication through standard input/output
- Verify integration with MCP clients (Cline IDE)
- Establish patterns that can be extended in future spikes

## Hypothesis
**We believe that:** The stdio transport provides the most straightforward path to understanding MCP server fundamentals, with minimal infrastructure requirements and direct integration into development tools.

**Because:** 
- Stdio is universally supported across platforms
- No network configuration or port management required
- Direct process-to-process communication is simple and reliable
- FastMCP abstracts away the complexity of the MCP protocol
- Perfect for IDE integration where the editor spawns the server process

**We'll know we're right when:** 
- The server starts successfully and accepts MCP protocol messages
- Tools can be called and return expected results
- Prompts can be invoked with parameters
- Resources can be accessed via URI
- Cline IDE can discover and use all three primitives
- The pattern scales to more complex servers in subsequent spikes

## Scope & Constraints
- **Time Box:** 4-6 hours for implementation and testing
- **Out of Scope:** 
  - HTTP/SSE transport mechanisms
  - Authentication/authorization
  - Stateless vs stateful session management (using default stateful)
  - Error recovery and resilience patterns
  - Production deployment considerations
- **Dependencies:** 
  - FastMCP library (mcp.server.fastmcp)
  - Python 3.10+
  - uv package manager
  - MCP client (Cline IDE or similar)

## Exploration Log
### Initial Setup
- Installed FastMCP via project dependencies
- Created minimal server script with 3 MCP primitives
- Chose descriptive names for demonstration purposes

### Core MCP Primitives Implementation

#### 1. Tool: `greet(name: str)`
- Simplest possible tool with single string parameter
- Returns formatted greeting message
- Demonstrates basic parameter passing and return values
- Shows function-as-tool pattern with `@mcp.tool()` decorator

#### 2. Prompt: `greet_user(name: str, style: str)`
- More complex with optional parameter (style defaults to "friendly")
- Demonstrates parameter validation via dictionary lookup
- Returns instruction string for LLM to execute
- Shows how prompts differ from tools (return instructions, not results)
- Three styles supported: friendly, formal, casual

#### 3. Resource: `example://test`
- Static resource accessible via URI scheme
- Demonstrates resource registration with `@mcp.resource()`
- Returns simple string content
- Shows URI-based access pattern

### Transport Configuration
- Used `stdio` transport for maximum simplicity
- Server reads from stdin, writes to stdout
- Compatible with process spawning patterns used by IDEs
- No ports, no networking, no certificates needed

### Integration Patterns
- Can be run directly: `uv run spikes/000_stdio/main_mcp_server.py`
- Can be configured in Cline's MCP settings
- Server lifecycle managed by parent process
- Clean shutdown on stdin close

## Key Insights
- **✅ Confirmed:** 
  - FastMCP dramatically simplifies MCP server creation
  - Stdio transport is ideal for local development and IDE integration
  - The decorator pattern (`@mcp.tool()`, `@mcp.prompt()`, `@mcp.resource()`) is intuitive
  - Type hints automatically become parameter schemas
  - Docstrings become tool/prompt/resource descriptions
  - Server startup is nearly instantaneous with stdio
  - No infrastructure (Docker, nginx) needed for basic functionality

- **❌ Challenged:** 
  - Initially unclear distinction between tools and prompts
  - Resource URI schemes need documentation (not obvious what's valid)
  - Error messages during development were sometimes cryptic
  - Stateful vs stateless distinction not immediately apparent

- **🤔 Questions Raised:** 
  - When should we use tools vs prompts?
  - What are the performance implications of stdio vs HTTP?
  - How do we handle long-running operations with stdio?
  - Can multiple clients connect to the same stdio server? (No - 1:1 relationship)
  - What's the right granularity for tools? (One per operation? Grouped?)

## Recommendation
**Status:** Complete

**Decision:** Adopt as the foundation for all MCP server development

**Rationale:** 
This spike successfully demonstrates that:
- MCP servers can be created with minimal boilerplate
- Stdio transport is perfect for development and IDE integration
- The three core primitives (tools, prompts, resources) cover most use cases
- FastMCP abstracts protocol complexity effectively
- Pattern established here scales to more complex servers

Every subsequent spike builds on this foundation:
- Spike 001: Adds multiple tools and resources
- Spike 002: Adds sophisticated logging
- Spike 003/004: Moves to HTTP transport with Docker
- Spike 005: Combines concepts for production use

**Next Steps:**
1. ✅ Document integration with Cline IDE
2. Explore error handling patterns (Spike 002)
3. Test with multiple simultaneous tool calls
4. Investigate session state management
5. Compare with HTTP transport performance (Spike 003)

## Reference Materials
- **Code Location:** `spikes/000_stdio/main_mcp_server.py`
  - Single file implementation (~60 lines)
  - Three example primitives (tool, prompt, resource)
  - Clean, documented code structure
  
- **Related Spikes:**
  - Foundation for all other spikes
  - Spike 001: Extended demos with more tools
  - Spike 002: Adds logging patterns
  - Spike 003: HTTP transport migration
  
- **External Resources:**
  - [FastMCP Documentation](https://github.com/jlowin/fastmcp)
  - [MCP Protocol Specification](https://modelcontextprotocol.io/)
  - [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
  - [Cline IDE Integration Guide](https://github.com/cline/cline)

## Usage

### Running the Server

#### Direct Execution
```bash
# From repository root
uv run spikes/000_stdio/main_mcp_server.py
```

#### Cline IDE Integration
Add to your Cline MCP settings (`cline_mcp_settings.json`):
```json
{
  "mcpServers": {
    "stdio": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-studies/spikes/000_stdio",
        "run",
        "main_mcp_server.py"
      ]
    }
  }
}
```

### Testing the Primitives

#### Tool: greet
```python
# Call from MCP client
greet(name="Alice")
# Returns: "Hello, Alice!"
```

#### Prompt: greet_user
```python
# Call from MCP client
greet_user(name="Bob", style="formal")
# Returns: "Please write a formal, professional greeting for someone named Bob."

greet_user(name="Carol")  # Uses default style
# Returns: "Please write a warm, friendly greeting for someone named Carol."
```

#### Resource: example://test
```python
# Access from MCP client
access_resource("example://test")
# Returns: "This is a test resource"
```

### Development Tips
- Server logs to stderr, so stdout remains clean for MCP protocol
- Use `Ctrl+C` or close stdin to terminate
- Check docstrings - they become tool/prompt descriptions
- Type hints define parameter schemas automatically
- Resource URIs can use any scheme (example://, file://, etc.)
