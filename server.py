import importlib.metadata as md
import os
import re
import time
from json import JSONDecodeError

import fastmcp
from fastmcp import Context, FastMCP
from fastmcp.server.dependencies import get_http_headers
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitRequestURLParams,
    ElicitResult,
    InputRequiredResult,
    ToolAnnotations,
)
from prefab_ui.components import Badge, Column, Heading, Muted
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

DEPLOYMENT_PROBE = "server-1.0.6"

mcp = FastMCP(
    name="Jake's Test Server 🚀",
    version="1.0.6",
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
            "deployment_probe": DEPLOYMENT_PROBE,
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
    tags={"demo", "response-size"},
    annotations=ToolAnnotations(
        title="Generate Sized Response",
        readOnlyHint=True,
        idempotentHint=True,
    ),
)
def generate_sized_response(size: str) -> str:
    """Return an ASCII payload of the requested size, such as 10KB or 5MB."""
    return "x" * _parse_response_size(size)


@mcp.tool(app=True, tags={"app", "demo"})
def mcp_app(name: str) -> Column:
    """Render a simple Prefab MCP App."""
    with Column(gap=3, css_class="p-8") as card:
        Heading(f"Hello, {name}!")
        Muted("Rendered as an MCP App using Prefab.")
        Badge("MCP App", variant="success")
    return card


@mcp.tool(tags={"demo", "elicitation", "form"})
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


@mcp.tool(tags={"demo", "elicitation", "url"})
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
