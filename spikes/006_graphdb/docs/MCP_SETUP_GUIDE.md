# Neo4j MCP Server Setup for Cline

## Overview

This guide explains how to connect your Cline MCP client to the Neo4j Vector Database through the MCP server.

## Architecture

```
Cline (Claude IDE Extension)
    ↓
MCP Protocol
    ↓
main_server.py (MCP Server)
    ↓
Neo4j (Port 7687)
    ↓
Your Documents & Embeddings
```

## Prerequisites

✅ Neo4j is running (docker-compose up -d)
✅ main_server.py is created (spikes/006_vectorDb/main_server.py)
✅ mcp package installed (already in dependencies)

## Step 1: Start the MCP Server

### Option A: Direct Python Execution
```bash
cd spikes/006_vectorDb
python3 main_server.py
```

### Option B: Using stdio transport (Recommended for Cline)
The server uses stdio transport, which is what Cline expects. You can verify it works:

```bash
cd spikes/006_vectorDb
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python3 main_server.py
```

## Step 2: Register MCP Server in Cline Settings

### Locate Cline Settings
1. Open Cline settings file in VS Code
2. Path: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

Or use the Cline UI:
- Click Cline extension icon
- Go to Settings (gear icon)
- Find MCP Servers section

### Add Neo4j MCP Server Configuration

Add this to your `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "vectordb": {
      "command": "python3",
      "args": [
        "/absolute/path/to/spikes/006_vectorDb/main_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Replace the path with your actual path:
```bash
# Get your absolute path:
cd spikes/006_vectorDb && pwd
# Copy the output and use it above
```

**Example (macOS):**
```json
{
  "mcpServers": {
    "vectordb": {
      "command": "python3",
      "args": [
        "/Users/bjenniskens/Developer/mcp-studies/spikes/006_vectorDb/main_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Step 3: Restart Cline

1. Close Cline extension (if open)
2. Reload VS Code window (Cmd+R on Mac, Ctrl+R on Windows/Linux)
3. Open Cline again - it will reconnect to the MCP server

## Step 4: Test the Connection

In Cline, you should now be able to use these tools:

### Test 1: Get Database Stats
```
Use the get_database_stats tool to show how many documents and chunks are in the Neo4j database
```

Cline should respond with:
```json
{
  "documents": X,
  "chunks": Y,
  "relationships": Z
}
```

### Test 2: Get All Documents
```
List all documents in the vector database
```

### Test 3: Search Chunks
```
Search for chunks containing the word "circuit"
```

## Available MCP Tools

Once connected, you can use these tools:

### 1. `get_all_documents`
Get all documents in the vector database
```
No parameters required
```

### 2. `search_chunks`
Search for chunks containing specific text
```
Parameters:
  - query (required): Text to search for
  - limit (optional): Max results (default: 5)
```

### 3. `get_document_chunks`
Get all chunks from a specific document
```
Parameters:
  - document_title (required): Title of the document
  - limit (optional): Max chunks to return (default: 10)
```

### 4. `get_database_stats`
Get statistics about the vector database
```
No parameters required
```

### 5. `search_by_keywords`
Search chunks containing any of the keywords
```
Parameters:
  - keywords (required): Array of keywords to search for
  - limit (optional): Max results (default: 5)
```

### 6. `get_embeddings_info`
Get information about embeddings files
```
No parameters required
```

## Troubleshooting

### Issue: MCP Server not connecting

**Check 1: Server is running**
```bash
ps aux | grep main_server.py
```

**Check 2: Neo4j is running**
```bash
docker-compose ps
```

**Check 3: Port 7687 is accessible**
```bash
lsof -i :7687
```

### Issue: "Tool not found" error

1. Verify `main_server.py` is in the correct location
2. Check the path in `cline_mcp_settings.json` is absolute (not relative)
3. Make sure Python can import `mcp`:
   ```bash
   python3 -c "import mcp; print('MCP module found')"
   ```

### Issue: "Connection refused" to Neo4j

1. Start Neo4j: `cd spikes/006_vectorDb && docker-compose up -d`
2. Wait 30 seconds for startup
3. Test connection: `docker-compose ps`

## Example Usage in Cline

### Chat with Cline about your documents:

**User:** "How many IC datasheets are loaded in the database?"

**Cline will:**
1. Call `get_all_documents` tool
2. Show you the documents
3. Call `get_database_stats` tool
4. Report the counts

**User:** "Search for information about timers"

**Cline will:**
1. Call `search_chunks` with query="timer"
2. Return relevant chunks
3. Summarize findings

## Advanced: Custom Queries

The MCP server translates Cline requests to Neo4j Cypher queries. For custom queries, you can modify `main_server.py` to add more tools.

## Logs and Debugging

Check MCP server logs in Cline's output panel:
1. Open Cline extension
2. Look for debug output in the terminal panel
3. Errors will show connection issues

## Persistence

The MCP server configuration is stored in:
- `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

This persists across VS Code sessions.

## Next Steps

1. ✅ Start Neo4j: `docker-compose up -d`
2. ✅ Configure MCP in Cline settings (use absolute path)
3. ✅ Restart Cline
4. ✅ Test with simple queries
5. ✅ Build conversational workflows with your documents

---

**Quick Start Command:**
```bash
# Terminal 1: Start Neo4j
cd spikes/006_vectorDb && docker-compose up -d

# Terminal 2: Optionally start server manually (Cline will auto-start it)
cd spikes/006_vectorDb && python3 main_server.py

# Then configure in Cline settings and reload VS Code
