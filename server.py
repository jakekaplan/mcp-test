import os
import time

import httpx
import fastmcp
from fastmcp import FastMCP
import importlib.metadata as md

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


if __name__ == '__main__':
    mcp.run(transport="streamable-http")
