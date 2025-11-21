# Testing the Graph Database MCP Server

This guide explains how to test your Graph Database MCP Server and why it is useful.

## 1. Automated Testing (Unit Tests)

We have already set up a comprehensive unit test suite. These tests check the logic of your server without needing the actual database running (using mocks).

**Run the tests:**

```bash
make unit-tests
```

**What this tests:**

- Server initialization.
- Tool definitions (`get_all_documents`, `search_chunks`, etc.).
- Error handling (e.g., what happens if the DB is down).
- Data pipeline logic (PDF extraction, chunking).

## 2. Manual Testing (Interactive)

To see the server in action, you can use the MCP Inspector. This allows you to interact with the tools directly in your browser.

**Prerequisites:**

- Node.js installed (for `npx`).
- The server must be running.

**Steps:**

1. **Start the server** (if not already running):

    ```bash
    make up
    ```

2. **Run the Inspector**:
    Since your server runs in Docker, we need to connect to it. However, the Inspector usually runs a local command.
    
    If you want to test the python script directly (bypassing Docker for the server part, but connecting to the Dockerized Neo4j):
    
    ```bash
    # Ensure dependencies are installed locally
    pip install mcp[cli] neo4j uvicorn

    # Run the inspector against your local script
    npx @modelcontextprotocol/inspector python main_server.py
    ```

    *Note: This works because `main_server.py` defaults to connecting to `localhost:7687`, which is where Docker exposes Neo4j.*

3. **Use the Tools**:
    - **`get_database_stats`**: Check if data is loaded.
    - **`get_all_documents`**: See what files are indexed.
    - **`search_chunks`**: Try searching for "PlayStation" or "datasheet".
    - **`get_document_chunks`**: Read the content of a specific file.

## 3. Why use a Graph Database with MCP?

Connecting an LLM (like Claude or a coding assistant) to a Graph Database via MCP provides powerful **Retrieval Augmented Generation (RAG)** capabilities.

### Benefits

1. **"Memory" for your AI**:
    - You can feed the AI thousands of pages of documentation (PDFs, manuals).
    - The AI doesn't need to read the whole file every time; it can search for just the relevant "chunks".

2. **Structured Knowledge**:
    - Unlike a simple text search, a Graph DB understands relationships: `Document -> contains -> Chunk`.
    - Future upgrades can add more complex relationships like `Chunk -> mentions -> Entity` (e.g., "Chunk 5 mentions 'CPU'").

3. **Precision**:
    - Instead of pasting a whole PDF into the chat, the MCP server lets the AI "look up" exactly what it needs to answer your question.

### Example Workflow

1. **User**: "How do I reset the PS3?"
2. **AI (via MCP)**: Calls `search_chunks(query="reset PS3")`.
3. **Server**: Returns 3 specific paragraphs from `ps3man.txt`.
4. **AI**: Reads those paragraphs and answers the user accurately.

## 4. Future Improvements (Vector Search)

Currently, your server uses **Keyword Search** (`CONTAINS`).
Your pipeline *already generates embeddings* (vector representations of text).

**Next Step**: Update `main_server.py` to use **Vector Search**.

- This allows "Semantic Search".
- Example: Searching for "controller" would also find "gamepad" or "joystick" because they have similar meanings, even if the exact word isn't there.
