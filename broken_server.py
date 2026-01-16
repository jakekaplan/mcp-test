from fastmcp import FastMCP

my_cool_server = FastMCP("broken")


@my_cool_server.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"
