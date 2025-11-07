# MCP Studies - Spikes Index

This directory contains various experimental spikes and proof-of-concepts for exploring MCP (Model Context Protocol) functionality.

## What is a Spike?

A **spike** is a concept from [Extreme Programming (XP)](http://www.extremeprogramming.org/rules/spike.html) - a time-boxed research activity designed to explore and reduce uncertainty around technical problems or user stories. 

In the context of this project, spikes serve to:
- 🔬 **Explore unknown technical territory** - Investigate MCP features, patterns, and capabilities
- 📚 **Gather information** - Learn how different MCP components work together
- ⚡ **Reduce risk** - Test assumptions and validate approaches before full implementation
- 🧪 **Experiment safely** - Try new ideas without affecting main codebase
- 📖 **Create reference material** - Build reusable examples and documentation

Each spike is **scoped**, **time-boxed** and **focused** on answering specific questions about MCP development, such as "How do we implement clean logging?" or "What's the best way to structure tools and prompts?"

## Overview

Each spike focuses on a specific aspect of MCP development, providing working examples, documentation, and tests that can be used as reference or starting points for further development. Unlike traditional prototypes, spikes are meant to be **exploratory** and **educational** - they may be thrown away once their knowledge goal is achieved, or evolved into production code. However, our approach is to remain keeping them part of the code base in a separate [spikes](../spikes) folder.

## Available Spikes

| Spike | Name | Description | Status | Key Features | Last Updated |
|-------|------|-------------|--------|--------------|--------------|
| **000** | [**Stdio Foundation**](./000_stdio/README.md) | Minimal MCP server using stdio transport - foundation for all other spikes | ✅ **Complete** | • Stdio transport<br>• Core MCP primitives<br>• IDE integration<br>• Simple & clean<br>• Reference implementation | 2025-11-05 |
| **001** | [**MCP Demos**](./001_demos/README.md) | Basic MCP server implementations with tools, prompts, and resources | ✅ **Complete** | • FastMCP server<br>• Tools & Resources<br>• Prompt templates<br>• HTTP endpoints<br>• Comprehensive tests | 2025-11-02 |
| **002** | [**Clean Logging**](./002_logging/README.md) | Production-ready MCP server with harmonized, noise-free logging | ✅ **Complete** | • Clean log output<br>• Noise suppression<br>• Professional formatting<br>• Development-friendly<br>• Production-ready | 2025-11-02 |
| **003** | [**Docker + SSL + NGINX**](./003_docker/README.md) | Production-like deployment with Docker containers, SSL/TLS, and NGINX gateway | ✅ **Complete** | • Docker containerization<br>• SSL/TLS with mkcert<br>• NGINX reverse proxy<br>• Docker Compose<br>• Makefile automation | 2025-11-03 |
| **004** | [**Post Office**](./004_post_office/README.md) | Package management system demonstrating structured CSV data handling with multiple query tools | ✅ **Complete** | • CSV data management<br>• 6 specialized tools<br>• Docker deployment<br>• Business logic demo<br>• Query patterns | 2025-11-07 |

## Spike status legend

| Status | Meaning |
|--------|---------|
| 🚧 **In Progress** | Currently being developed |
| ✅ **Complete** | Fully implemented and documented |
| 🔬 **Experimental** | Proof of concept, may be unstable |
| 📚 **Reference** | Stable reference implementation |
| ⚠️ **Deprecated** | No longer maintained |
| 🔄 **Updated** | Recently updated or improved |


## Adding new spikes

When creating a new spike, follow this structure:

```
spikes/XXX_spike_name/
├── README.md          # Spike-specific documentation with they hypothesis
├── main_mcp_server.py     # Main spike solution
├── test_*.py          # (Unit) Tests for the spike
└── try_*.py           # (Exploratory) local tests for the spike
```

### Spike naming convention
- Use 3-digit zero-padded numbers: `001`, `002`, `003`, etc.
- Use descriptive names separated by underscores
- Examples: `003_authentication`, `004_streaming_data`, `005_complex_workflows`

### Required documentation
Each spike should include:
- **Purpose** - What problem does this spike solve?
- **How to run** - Clear startup instructions
- **What to expect** - Expected behavior and output
- **Key learnings** - What insights were gained
- **Integration notes** - How to use in other projects

### Updating this index
When adding a new spike:
1. Add a new row to the table above
2. Include appropriate status and key features
3. Update the "Last Updated" date
4. Add quick start instructions if needed

## Integration with main project

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

## Related resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp)

---

> 💡 **Tip**: Each spike is self-contained and can be run independently. Start with the README in each spike directory for specific instructions.
