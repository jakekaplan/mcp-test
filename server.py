from fastmcp import FastMCP
from fastmcp import Context
from typing import Annotated, cast
from dataclasses import dataclass
from mcp.types import TextContent

mcp = FastMCP("Integration Tests 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

@mcp.tool
def echo(message: str) -> str:
    """Echo back a message"""
    return message

@mcp.resource("message://hello")
def hello_message() -> str:
    """A simple hello message resource"""
    return "Hello from the resource!"

@mcp.prompt
def greeting_prompt(name: Annotated[str, "Name to greet"]) -> str:
    """Generate a greeting prompt"""
    return f"Please greet {name} in a friendly way"

@mcp.prompt
def math_prompt(
    operation: Annotated[str, "Operation to perform (add/multiply)"],
    x: Annotated[int, "First number"],
    y: Annotated[int, "Second number"]
) -> str:
    """Generate a math operation prompt"""
    return f"Please {operation} the numbers {x} and {y}"

@dataclass
class Person:
    name: str

@mcp.tool
async def ask_for_name(context: Context) -> str:
    """Ask for user's name using elicitation"""
    result = await context.elicit(
        message="What is your name?",
        response_type=Person,
    )
    if result.action == "accept":
        return f"Hello, {result.data.name}!"
    else:
        return "No name provided."

@mcp.tool
async def progress_tool(context: Context) -> int:
    """Tool that reports progress"""
    for i in range(3):
        await context.report_progress(
            progress=i + 1,
            total=3,
            message=f"{(i + 1) / 3 * 100:.2f}% complete"
        )
    return 100

@mcp.tool
async def simple_sample(message: str, context: Context) -> str:
    """Simple sampling tool"""
    result = await context.sample("Hello, world!")
    return cast(TextContent, result).text

mcp = FastMCP("Integration Tests 🚀")


if __name__ == '__main__':
    mcp.run(transport="stdio")
