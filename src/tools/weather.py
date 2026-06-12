# get_weather tool func definition
def get_weather(city: str):
    if city == "Paris":
        return "it's sunny in Paris"
    else:
        return {"city": city, "temperature": 22}


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
