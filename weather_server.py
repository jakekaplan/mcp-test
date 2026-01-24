from fastmcp import FastMCP

mcp = FastMCP("Weather Server")

@mcp.tool()
def weather_tool(city: str) -> str:
    """Get weather information for a city"""
    weather_data = {
        "Hyderabad": "Sunny, 32°C",
        "London": "Rainy, 15°C",
        "Tokyo": "Cloudy, 22°C"
    }
    return weather_data.get(city, f"Weather data not available for {city}")
