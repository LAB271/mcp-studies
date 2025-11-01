# mcp-studies

Open studio on MCP servers - experimental studies and prototypes using the Model Context Protocol (MCP) Python SDK. This repository provides a reproducible environment for testing, development, and integration of MCP features.

[![Python 3.13](https://img.shields.io/badge/python-v3.13-blue.svg)](https://www.python.org/downloads/release/python-3137/)

## Project Setup and Structure

### Environment Setup

To create a clean Python environment for this project, we use [uv](https://github.com/astral-sh/uv) for fast dependency management and virtual environment creation.

**Steps:**

1. **Create a virtual environment:**
   ```bash
   uv venv
   ```
   This will create a `.venv` directory with an isolated Python environment.

2. **Install dependencies:**
   ```bash
   make env
   ```
   This command (defined in the `Makefile`) installs all required packages into the `.venv` environment.

3. **Activate the environment:**
   ```bash
   source .venv/bin/activate
   ```
   This sets your shell to use the project's Python and installed packages.

### The `spikes` Folder

The `spikes` directory contains experimental code, demos, and proof-of-concept scripts. Each subfolder or script is a "spike"—a focused experiment or prototype to explore a specific feature, integration, or idea. Spikes are not production code; they are intended for learning, rapid iteration, and sharing findings.

### Environment Variables

Use the included `env.sh` script to automatically generate a `.env` file with necessary API keys from 1Password:

```bash
./env.sh          # Silent mode
./env.sh -v       # Verbose mode
source .env       # Load environment variables
```

Configure your credentials in `.env_vars` file following the format:
```
ENV_VAR_NAME:1password_item_name:field_name
``` 
