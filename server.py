import importlib.metadata as md
import os
import time
from json import JSONDecodeError

import fastmcp
from fastmcp import Context, FastMCP
from fastmcp.server.dependencies import get_http_headers
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitResult,
    InputRequiredResult,
    ToolAnnotations,
)
from prefab_ui.components import Badge, Column, Heading, Muted
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

mcp = FastMCP(
    name="Jake's Test Server 🚀",
    version="1.0.5",
    website_url="https://jakekaplan.dev/",
    instructions=(
        "Use this demo server to test MCP tools, resources, prompts, apps, "
        "modern elicitation, annotations, tags, and component versioning. "
        "The tools are intentionally varied and may include errors or large results."
    ),
)


@mcp.custom_route("/test", methods=["GET", "POST"])
async def test_route(request: Request) -> Response:
    payload = None

    if request.method == "POST":
        try:
            payload = await request.json()
        except JSONDecodeError:
            payload = {"raw": (await request.body()).decode("utf-8", errors="replace")}

    return JSONResponse(
        {
            "status": "ok",
            "service": "Jake's Test Server 🚀",
            "method": request.method,
            "request_id": request.headers.get("x-request-id"),
            "query_params": dict(request.query_params),
            "payload": payload,
        }
    )


@mcp.tool(
    name="echo",
    version="1.0",
    tags={"demo", "text"},
    annotations=ToolAnnotations(title="Echo Message v1", readOnlyHint=True),
)
def echo_v1(message: str) -> str:
    """Echo back a message unchanged."""
    return message


@mcp.tool(
    name="echo",
    version="2.0",
    tags={"demo", "text"},
    annotations=ToolAnnotations(title="Echo Message v2", readOnlyHint=True),
)
def echo_v2(message: str) -> str:
    """Echo back a message with a v2 prefix."""
    return f"Echo v2: {message}"


@mcp.tool(app=True, tags={"app", "demo"})
def greeting_card(name: str = "Inspector") -> Column:
    """Render a simple greeting card as an MCP App."""
    with Column(gap=3, css_class="p-8") as card:
        Heading(f"Hello, {name}!")
        Muted("Rendered as an MCP App using Prefab.")
        Badge("MCP App", variant="success")
    return card


@mcp.tool(tags={"demo", "elicitation"})
async def introduce_yourself(ctx: Context) -> str | InputRequiredResult:
    """Ask the user for an introduction using modern MCP elicitation."""
    responses = ctx.input_responses
    if responses is None or "introduction" not in responses:
        return InputRequiredResult(
            input_requests={
                "introduction": ElicitRequest(
                    params=ElicitRequestFormParams(
                        message="Tell the test server a little about yourself.",
                        requested_schema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "title": "Display name",
                                },
                                "mood": {
                                    "type": "string",
                                    "title": "Current mood",
                                    "enum": ["curious", "focused", "excited"],
                                    "default": "curious",
                                },
                            },
                            "required": ["name", "mood"],
                        },
                    )
                )
            }
        )

    answer = responses["introduction"]
    if not isinstance(answer, ElicitResult) or answer.action == "decline":
        return "Introduction declined."
    if answer.action == "cancel" or answer.content is None:
        return "Introduction cancelled."

    name = str(answer.content["name"])
    mood = str(answer.content["mood"])
    return f"Nice to meet you, {name}! You're feeling {mood}."


@mcp.tool(tags={"demo", "large-output", "text"})
def big_result(n: int) -> str:
    """Return a potentially very large string made by repeating “bigtool” n times: bigtoolbigtoolbigtoolbigtoolbigtoolbigtoolbigtoolbigtoolbigtoolbigtool. Use this tool to exercise clients with a sizeable text result, test long tool descriptions, inspect wrapping and truncation behavior, and confirm that large MCP tool responses remain usable when the requested repetition count grows."""
    return "bigtool" * n


@mcp.tool(
    tags={"demo", "math"},
    annotations=ToolAnnotations(title="Add Numbers", idempotentHint=True),
)
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool
def version() -> str:
    """Get the fastmcp version"""
    return fastmcp.__version__


@mcp.tool(
    tags={"dangerous", "demo"},
    annotations=ToolAnnotations(title="Raise an Error", destructiveHint=True),
)
def error() -> str:
    """Raise an error"""
    raise ValueError("It's all going wrong!!!")


@mcp.tool
def env() -> dict[str, str]:
    """Get the env"""
    return {k: v for k, v in os.environ.items()}


@mcp.tool
def get_headers() -> dict[str, str]:
    """Get all HTTP headers for the current request"""
    return get_http_headers(include_all=True)


@mcp.tool
def sleep() -> dict[str, str]:
    """Sleep forever"""
    while True:
        time.sleep(1)


@mcp.tool(
    tags={"demo", "packages"},
    annotations=ToolAnnotations(title="Package Versions", openWorldHint=True),
)
def pkg_versions() -> list[str]:
    """List installed Python packages and versions"""
    entries: list[str] = []
    for dist in md.distributions():
        name = dist.metadata.get("Name", "unknown")
        version = dist.version
        entries.append(f"{name}=={version}")
    entries.sort(key=lambda s: s.lower())
    return entries


@mcp.prompt
def greeting(name: str) -> str:
    """Generate a greeting prompt"""
    return f"Please greet {name} in a friendly and enthusiastic way."


@mcp.resource("config://app")
def get_app_config() -> str:
    """Get the application configuration"""
    return "app_name: Jake's Test Server\nversion: 1.0.0\ndebug: true"


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Get a user's profile by ID"""
    return f"user_id: {user_id}\nname: User {user_id}\nemail: user{user_id}@example.com"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
