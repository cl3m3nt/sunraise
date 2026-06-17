import requests


_WMO = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


class GeocodeError(Exception):
    pass


def _geocode(city: str) -> tuple[float, float, str]:
    """Geocode a city name to (lat, lon, name) via Open-Meteo."""
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        raise GeocodeError(f"city not found: {city}")
    loc = results[0]
    return loc["latitude"], loc["longitude"], loc["name"]


def get_weather(city: str) -> dict:
    """Current weather for a city, via Open-Meteo. This tool func is used for the API calls."""
    try:
        lat, lon, name = _geocode(city)
    except GeocodeError as e:
        return {"error": str(e)}
    except requests.RequestException as e:
        return {"error": f"geocoding failed: {e}"}

    try:
        # We can try to get more info, check https://open-meteo.com/en/docs
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10,
        )
        r.raise_for_status()
        cur = r.json()["current"]
    except requests.RequestException as e:
        return {"error": f"weather fetch failed: {e}"}

    return {
        "city": name,
        "temp_c": cur["temperature_2m"],
        "feels_like_c": cur["apparent_temperature"],
        "wind_kmh": cur["wind_speed_10m"],
        "description": _WMO.get(cur["weather_code"], "unknown"),
    }


# get_weather tool config definition
weather_tool = {
    "name": "get_weather",
    "description": "Get the current weather for a city",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    },
}

# get_weather tool config definition for mistral
mistral_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}

# get_weather tool config definition for openai
openai_weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "Get current weather for a city",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}
