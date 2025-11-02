# MCP Studies - Spikes Index

This directory contains various experimental spikes and proof-of-concepts for exploring MCP (Model Context Protocol) functionality.

## Overview

Each spike focuses on a specific aspect of MCP development, providing working examples, documentation, and tests that can be used as reference or starting points for further development.

## Available Spikes

| Spike | Name | Description | Status | Key Features | Last Updated |
|-------|------|-------------|--------|--------------|--------------|
| **001** | [**MCP Demos**](./001_demos/) | Basic MCP server implementations with tools, prompts, and resources | ✅ **Complete** | • FastMCP server<br>• Tools & Resources<br>• Prompt templates<br>• HTTP endpoints<br>• Comprehensive tests | 2025-11-02 |
| **002** | [**Clean Logging**](./002_logging/) | Production-ready MCP server with harmonized, noise-free logging | ✅ **Complete** | • Clean log output<br>• Noise suppression<br>• Professional formatting<br>• Development-friendly<br>• Production-ready | 2025-11-02 |

## Spike Status Legend

| Status | Meaning |
|--------|---------|
| 🚧 **In Progress** | Currently being developed |
| ✅ **Complete** | Fully implemented and documented |
| 🔬 **Experimental** | Proof of concept, may be unstable |
| 📚 **Reference** | Stable reference implementation |
| ⚠️ **Deprecated** | No longer maintained |
| 🔄 **Updated** | Recently updated or improved |

## Quick Start

### Spike 001 - MCP Demos
```bash
# Start the basic MCP server
uv run spikes/001_demos/stream_config.py

# Run comprehensive tests
uv run python -m pytest spikes/001_demos/test_stream_config.py -v
```

### Spike 002 - Clean Logging
```bash
# Start the clean server with minimal logging
uv run spikes/002_logging/clean_server.py
```

## Usage Patterns

### For Learning MCP
- Start with **Spike 001** for basic MCP concepts
- Review tests to understand expected behavior
- Experiment with tools, prompts, and resources

### For Production Use
- Use **Spike 002** as a template for production servers
- Copy the clean logging configuration
- Adapt the server structure for your use case

### For Development
- Both spikes include error handling patterns
- Test examples show proper MCP client implementation
- Logging configurations suitable for debugging

## Adding New Spikes

When creating a new spike, follow this structure:

```
spikes/XXX_spike_name/
├── README.md           # Spike-specific documentation
├── main_server.py      # Primary server implementation
├── test_*.py          # Tests for the spike
├── examples/          # Usage examples (optional)
└── docs/              # Additional documentation (optional)
```

### Spike Naming Convention
- Use 3-digit zero-padded numbers: `001`, `002`, `003`, etc.
- Use descriptive names separated by underscores
- Examples: `003_authentication`, `004_streaming_data`, `005_complex_workflows`

### Required Documentation
Each spike should include:
- **Purpose** - What problem does this spike solve?
- **How to run** - Clear startup instructions
- **What to expect** - Expected behavior and output
- **Key learnings** - What insights were gained
- **Integration notes** - How to use in other projects

### Updating This Index
When adding a new spike:
1. Add a new row to the table above
2. Include appropriate status and key features
3. Update the "Last Updated" date
4. Add quick start instructions if needed

## Integration with Main Project

These spikes serve as:
- **Learning resources** for MCP development
- **Reference implementations** for common patterns
- **Testing grounds** for new features
- **Documentation examples** for best practices

## Contributing

When contributing to spikes:
1. Follow the existing structure and naming conventions
2. Include comprehensive tests
3. Document all functionality clearly
4. Update this index with your changes
5. Ensure examples work out of the box

## Related Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp)

---

> 💡 **Tip**: Each spike is self-contained and can be run independently. Start with the README in each spike directory for specific instructions.