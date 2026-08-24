import asyncio
import importlib.metadata as md
import os
import re

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitRequestURLParams,
    ElicitResult,
    InputRequiredResult,
    ToolAnnotations,
)

mcp = MCPServer(
    name="Jake's Test Server 🚀",
    version="1.0.5",
    website_url="https://jakekaplan.dev/",
    instructions=(
        "Use this demo server to test MCP tools, resources, prompts, modern "
        "elicitation, annotations, and varied tool results. Some tools "
        "intentionally return errors, large responses, or never complete."
    ),
)


@mcp.tool(
    name="echo",
    annotations=ToolAnnotations(title="Echo Message", read_only_hint=True),
)
def echo_message(message: str) -> str:
    """Echo back a message unchanged."""
    return message


MAX_RESPONSE_BYTES = 100 * 1024 * 1024
_RESPONSE_SIZE_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(b|kb|mb)$", re.IGNORECASE)


def _parse_response_size(size: str) -> int:
    match = _RESPONSE_SIZE_PATTERN.fullmatch(size.strip())
    if match is None:
        raise ValueError("Size must use B, KB, or MB, for example: 500B, 10KB, or 5MB")

    amount, unit = match.groups()
    multipliers = {"b": 1, "kb": 1024, "mb": 1024 * 1024}
    byte_count = round(float(amount) * multipliers[unit.lower()])
    if byte_count < 1:
        raise ValueError("Size must be at least 1 byte")
    if byte_count > MAX_RESPONSE_BYTES:
        raise ValueError("Size must not exceed 100MB")
    return byte_count


@mcp.tool(
    annotations=ToolAnnotations(
        title="Generate Sized Response",
        read_only_hint=True,
        idempotent_hint=True,
    )
)
def generate_sized_response(size: str) -> str:
    """Return an ASCII payload of the requested size, such as 10KB or 5MB."""
    return "x" * _parse_response_size(size)


@mcp.tool()
async def form_elicitation(ctx: Context) -> str | InputRequiredResult:
    """Customize a greeting using modern form-mode MCP elicitation."""
    responses = ctx.input_responses
    if responses is None or "greeting" not in responses:
        return InputRequiredResult(
            input_requests={
                "greeting": ElicitRequest(
                    params=ElicitRequestFormParams(
                        message="Customize the greeting this demo tool should return.",
                        requested_schema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "title": "Who should be greeted?",
                                    "description": "The name to use in the greeting.",
                                },
                                "style": {
                                    "type": "string",
                                    "title": "Greeting style",
                                    "description": "Choose the tone of the greeting.",
                                    "enum": ["friendly", "formal", "enthusiastic"],
                                    "default": "friendly",
                                },
                                "include_emoji": {
                                    "type": "boolean",
                                    "title": "Include an emoji?",
                                    "description": "Add a waving-hand emoji to the greeting.",
                                    "default": True,
                                },
                            },
                            "required": ["name"],
                        },
                    )
                )
            }
        )

    answer = responses["greeting"]
    if not isinstance(answer, ElicitResult) or answer.action == "decline":
        return "Greeting customization declined."
    if answer.action == "cancel" or answer.content is None:
        return "Greeting customization cancelled."

    name = str(answer.content["name"])
    style = str(answer.content.get("style", "friendly"))
    greetings = {
        "friendly": f"Hi, {name}! Great to meet you!",
        "formal": f"Hello, {name}. It is a pleasure to meet you.",
        "enthusiastic": f"Hey, {name}! It's fantastic to meet you!",
    }
    greeting = greetings.get(style, greetings["friendly"])
    if answer.content.get("include_emoji", True):
        greeting += " 👋"
    return greeting


@mcp.tool()
async def url_elicitation(ctx: Context) -> str | InputRequiredResult:
    """Demonstrate modern URL-mode MCP elicitation with a fake URL."""
    responses = ctx.input_responses
    if responses is None or "open_url" not in responses:
        return InputRequiredResult(
            input_requests={
                "open_url": ElicitRequest(
                    params=ElicitRequestURLParams(
                        message="Open a fake URL to test URL elicitation.",
                        url="https://example.invalid/mcp-url-elicitation",
                    )
                )
            }
        )

    answer = responses["open_url"]
    if not isinstance(answer, ElicitResult) or answer.action == "decline":
        return "URL elicitation declined."
    if answer.action == "cancel":
        return "URL elicitation cancelled."
    return "URL elicitation accepted."


@mcp.tool(
    name="add",
    annotations=ToolAnnotations(title="Add Numbers", idempotent_hint=True),
)
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool(name="version")
def get_sdk_version() -> str:
    """Get the official MCP Python SDK version."""
    return md.version("mcp")


@mcp.tool(
    name="error",
    annotations=ToolAnnotations(title="Raise an Error", destructive_hint=True),
)
def raise_tool_error() -> str:
    """Raise an intentional error."""
    raise ValueError("It's all going wrong!!!")


@mcp.tool(name="env")
def get_environment() -> dict[str, str]:
    """Get the server environment."""
    return dict(os.environ)


@mcp.tool(name="get_headers")
def get_request_headers(ctx: Context) -> dict[str, str]:
    """Get all HTTP headers for the current request."""
    return dict(ctx.headers or {})


@mcp.tool(name="sleep")
async def sleep_forever() -> None:
    """Sleep forever without blocking other server requests."""
    while True:
        await asyncio.sleep(1)


@mcp.tool(
    name="pkg_versions",
    annotations=ToolAnnotations(title="Package Versions", open_world_hint=True),
)
def list_package_versions() -> list[str]:
    """List installed Python packages and versions."""
    entries: list[str] = []
    for dist in md.distributions():
        name = dist.metadata.get("Name", "unknown")
        entries.append(f"{name}=={dist.version}")
    entries.sort(key=str.lower)
    return entries


@mcp.prompt(name="greeting")
def greeting_prompt(name: str) -> str:
    """Generate a greeting prompt."""
    return f"Please greet {name} in a friendly and enthusiastic way."


@mcp.resource("config://app")
def get_app_config() -> str:
    """Get the application configuration."""
    return "app_name: Jake's Test Server\nversion: 1.0.0\ndebug: true"


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Get a user's profile by ID."""
    return f"user_id: {user_id}\nname: User {user_id}\nemail: user{user_id}@example.com"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
