import os
import asyncio
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.sampling import RequestContext, SamplingMessage, SamplingParams

SERVER_URL = os.environ.get("TEST_MCP_SERVER_URL", "http://localhost:8000/mcp/")


async def test_ping_http():
    """Test basic connectivity with HTTP transport."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        result = await client.ping()
        assert result is True


async def test_list_tools():
    """Test listing available tools."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        tools = await client.list_tools()
        
        # Check we have all expected tools
        tool_names = [tool.name for tool in tools]
        assert "add" in tool_names
        assert "multiply" in tool_names
        assert "greet" in tool_names
        assert "echo" in tool_names
        
        # Check tool details
        add_tool = next(t for t in tools if t.name == "add")
        assert add_tool.description == "Add two numbers"


async def test_call_add_tool():
    """Test calling the add tool."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        result = await client.call_tool("add", {"a": 5, "b": 3})
        
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        assert result.content[0].text == "8"


async def test_call_multiply_tool():
    """Test calling the multiply tool."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        result = await client.call_tool("multiply", {"a": 4, "b": 7})
        
        assert hasattr(result, 'content')
        assert result.content[0].text == "28"


async def test_call_greet_tool():
    """Test calling the greet tool."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        result = await client.call_tool("greet", {"name": "FastMCP"})
        
        assert hasattr(result, 'content')
        assert result.content[0].text == "Hello, FastMCP!"


async def test_call_echo_tool():
    """Test calling the echo tool."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        test_message = "Testing echo functionality"
        result = await client.call_tool("echo", {"message": test_message})
        
        assert hasattr(result, 'content')
        assert result.content[0].text == test_message


async def test_multiple_sequential_calls():
    """Test making multiple sequential tool calls."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        # First call
        result1 = await client.call_tool("add", {"a": 10, "b": 20})
        assert result1.content[0].text == "30"
        
        # Second call
        result2 = await client.call_tool("multiply", {"a": 5, "b": 6})
        assert result2.content[0].text == "30"
        
        # Third call
        result3 = await client.call_tool("greet", {"name": "World"})
        assert result3.content[0].text == "Hello, World!"


async def test_concurrent_calls():
    """Test making concurrent tool calls."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        # Create multiple concurrent tasks
        tasks = [
            client.call_tool("add", {"a": i, "b": i + 1})
            for i in range(5)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify results
        for i, result in enumerate(results):
            expected = str(i + i + 1)
            assert result.content[0].text == expected


async def test_list_resources():
    """Test listing available resources."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        resources = await client.list_resources()
        
        # Check we have expected resources
        resource_uris = [str(r.uri) for r in resources]
        assert "message://hello" in resource_uris


async def test_read_resource():
    """Test reading a resource."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        # Read hello message resource
        result = await client.read_resource("message://hello")
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].text == "Hello from the resource!"


async def test_list_prompts():
    """Test listing available prompts."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        prompts = await client.list_prompts()
        
        # Check we have expected prompts
        prompt_names = [p.name for p in prompts]
        assert "greeting_prompt" in prompt_names
        assert "math_prompt" in prompt_names
        
        # Check prompt details
        greeting_prompt = next(p for p in prompts if p.name == "greeting_prompt")
        assert greeting_prompt.description == "Generate a greeting prompt"


async def test_get_prompt():
    """Test getting a prompt with arguments."""
    async with Client(
        transport=StreamableHttpTransport(SERVER_URL)
    ) as client:
        # Test greeting prompt
        result = await client.get_prompt("greeting_prompt", {"name": "Alice"})
        assert hasattr(result, 'messages')
        assert len(result.messages) > 0
        assert "Please greet Alice in a friendly way" in result.messages[0].content.text
        
        # Test math prompt
        result = await client.get_prompt("math_prompt", {
            "operation": "add",
            "x": 10,
            "y": 20
        })
        assert "Please add the numbers 10 and 20" in result.messages[0].content.text


async def test_progress():
    """Test progress reporting functionality."""
    progress_messages = []

    async def progress_handler(progress, total, message):
        progress_messages.append({
            "progress": progress,
            "total": total,
            "message": message
        })

    async with Client(
            transport=StreamableHttpTransport(SERVER_URL),
            progress_handler=progress_handler
    ) as client:
        result = await client.call_tool("progress_tool", {})
        assert result.content[0].text == "100"

        # Verify progress messages
        assert len(progress_messages) == 3
        assert progress_messages[0] == {"progress": 1, "total": 3, "message": "33.33% complete"}
        assert progress_messages[1] == {"progress": 2, "total": 3, "message": "66.67% complete"}
        assert progress_messages[2] == {"progress": 3, "total": 3, "message": "100.00% complete"}


async def test_elicitation_accept_content():
    """Test basic elicitation functionality."""
    async def elicitation_handler(message, response_type, params, ctx):
        return ElicitResult(action="accept", content=response_type(name="Alice"))

    async with Client(
        transport=StreamableHttpTransport(SERVER_URL),
        elicitation_handler=elicitation_handler
    ) as client:
        result = await client.call_tool("ask_for_name", {})
        assert result.content[0].text == "Hello, Alice!"


async def test_elicitation_decline():
    """Test that elicitation handler receives correct parameters."""
    async def elicitation_handler(message, response_type, params, ctx):
        return ElicitResult(action="decline")

    async with Client(
        transport=StreamableHttpTransport(SERVER_URL),
        elicitation_handler=elicitation_handler
    ) as client:
        result = await client.call_tool("ask_for_name", {})
        assert result.content[0].text == "No name provided."


async def test_sampling():
    """Test sampling functionality."""
    def sampling_handler(
        messages: list[SamplingMessage], params: SamplingParams, ctx: RequestContext
    ) -> str:
        return "This is the sample message!"

    async with Client(
        transport=StreamableHttpTransport(SERVER_URL),
        sampling_handler=sampling_handler
    ) as client:
        result = await client.call_tool("simple_sample", {"message": "Hello, world!"})
        assert result.content[0].text == "This is the sample message!"