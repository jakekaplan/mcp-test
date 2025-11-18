from fastmcp import FastMCP

mcp = FastMCP("Notify Server")


@mcp.tool
def slack_notify(message: str) -> str:
    """Send a message to slack"""
    print(message)
    return "Notification Sent!"

