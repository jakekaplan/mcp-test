import time
s = time.time()
from fastmcp import FastMCP
e = time.time()
print("IMPORT TOOK: e-s")

import os

import fastmcp

from fastmcp import Context
from typing import Annotated, cast
from dataclasses import dataclass
from mcp.types import TextContent
import pandas as pd
import importlib.metadata as md

mcp = FastMCP("Integration Tests 🚀")



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
def env() -> dict[str, str]:
    """Get the env"""
    return {k: v for k, v in os.environ.items()}

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


if __name__ == '__main__':
    mcp.run(transport="streamable-http")
