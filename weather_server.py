import time

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Starter MCP")


def request_with_retry(method: str, url: str, retries: int = 3, **kwargs) -> httpx.Response:
    """Make an HTTP request with retries."""
    for attempt in range(retries):
        try:
            response = httpx.request(method, url, timeout=5, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TimeoutException):
            if attempt == retries - 1:
                raise
            time.sleep(0.5 * (attempt + 1))
    raise httpx.HTTPError("Max retries exceeded")


@mcp.tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_response = request_with_retry("GET", geocode_url, params={"name": city, "count": 1})
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return f"Could not find location: {city}"

    location = geo_data["results"][0]
    lat, lon = location["latitude"], location["longitude"]
    name = location.get("name", city)

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_response = request_with_retry(
        "GET",
        weather_url,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "temperature_unit": "fahrenheit",
        },
    )
    weather_data = weather_response.json()

    current = weather_data.get("current", {})
    temp = current.get("temperature_2m", "unknown")
    code = current.get("weather_code", 0)

    conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
    }.get(code, "Unknown conditions")

    return f"{name}: {temp}°F, {conditions}"


if __name__ == "__main__":
    mcp.run()
