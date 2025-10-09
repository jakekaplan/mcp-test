import os
import time
import fastmcp
from fastmcp import FastMCP
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

@mcp.resource("substack://notes-extractor")
def extended_substack_notes_extractor() -> str:
    """Browser script to extract all historical Substack notes with detailed stats as JSON"""
    return """# Substack Notes Extractor - Browser Script

The Substack Notes Extractor is a browser-based JavaScript tool that extracts all your historical Substack notes with comprehensive performance metrics. 

**Get the script:** https://github.com/aboyalejandro/substack-notes-extractor/blob/main/get_notes.js

"""

if __name__ == '__main__':
    mcp.run(transport="streamable-http")
