# MCP Functionality Test

This project tests basic MCP (Model Context Protocol) functionality using FastMCP. It demonstrates simple tool calling, resource handling, prompts, elicitation, progress reporting, and sampling.

## MCP Features Tested

- **Tools**: Basic math operations (add, multiply), text operations (greet, echo)
- **Resources**: Simple message resource access
- **Prompts**: Template-based prompt generation
- **Elicitation**: User input collection with accept/decline handling
- **Progress**: Progress reporting during tool execution
- **Sampling**: Basic sampling functionality

## Running the Server

```bash
uv run test_server.py
```

The server runs on `http://localhost:8000/mcp/` by default.

## Running Tests

```bash
TEST_MCP_SERVER_URL=http://localhost:8000/mcp/ pytest test_client.py
```

Or set the environment variable and run:

```bash
export TEST_MCP_SERVER_URL=http://localhost:8000/mcp/
pytest test_client.py
```