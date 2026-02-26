import asyncio
import importlib.metadata as md
import os
import time

import fastmcp
import httpx
from fastmcp import Context, FastMCP
from mcp.types import Icon

mcp = FastMCP("Jake's Test Server 🚀")


@mcp.tool
def echo(message: str) -> str:
    """Echo back a message"""
    return message

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def version() -> str:
    """Get the fastmcp version"""
    return fastmcp.__version__

@mcp.tool
def error() -> str:
    """Raise an error"""
    raise ValueError("It's all going wrong!!!")

@mcp.tool
def env() -> dict[str, str]:
    """Get the env"""
    return {k: v for k, v in os.environ.items()}

@mcp.tool
def sleep() -> dict[str, str]:
    """Sleep forever"""
    while True:
        time.sleep(1)


@mcp.tool
async def stream_progress_demo(
    ctx: Context,
    steps: int = 8,
    delay_seconds: float = 0.75,
    fail_at: int | None = None,
) -> dict[str, str]:
    """Emit progress and log notifications over time for streaming tests."""
    await ctx.info(f"starting stream test: steps={steps}, delay={delay_seconds}s")

    for step in range(1, steps + 1):
        await asyncio.sleep(delay_seconds)
        await ctx.report_progress(step, steps, f"step {step}/{steps}")
        await ctx.info(f"heartbeat {step}/{steps}")

        if fail_at is not None and step == fail_at:
            await ctx.error(f"intentional failure at step {step}")
            raise RuntimeError(f"intentional failure at step {step}")

    await ctx.info("stream test complete")
    return {"status": "ok"}


@mcp.tool
def pkg_versions() -> list[str]:
    """List installed Python packages and versions"""
    entries: list[str] = []
    for dist in md.distributions():
        name = dist.metadata.get("Name", "unknown")
        version = dist.version
        entries.append(f"{name}=={version}")
    entries.sort(key=lambda s: s.lower())
    return entries


@mcp.tool
def ping_remote() -> dict:
    """Ping the ngrok endpoint"""
    response = httpx.get("https://semipreserved-jack-nontyrannously.ngrok-free.dev")
    return {"status_code": response.status_code, "text": response.text}


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


if __name__ == '__main__':
    mcp.run(transport="streamable-http")
