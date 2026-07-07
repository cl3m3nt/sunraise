from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_time(timezone: str):
    return datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M:%S %Z%z")


# get_current_time config definition for google
google_current_time_tool = {
    "name": "get_current_time",
    "description": "Get the current date and time for a timezone",
    "parameters": {
        "type": "object",
        "properties": {"timezone": {"type": "string", "description": "timezone name"}},
        "required": ["timezone"],
    },
}


# get_current_time config definition for gemma4
gemma4_current_time_tool = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current date and time for a timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "timezone name"}
            },
        },
        "required": ["timezone"],
    },
}


# get_current_time config definition for mistral
mistral_current_time_tool = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current date and time for a timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "timezone name"}
            },
            "required": ["timezone"],
        },
    },
}

# get_current_time config definition for openai
openai_current_time_tool = {
    "type": "function",
    "name": "get_current_time",
    "description": "Get the current date and time for a timezone",
    "parameters": {
        "type": "object",
        "properties": {"timezone": {"type": "string", "description": "timezone name"}},
        "required": ["timezone"],
    },
}

# get_current_time config definition for anthropic
anthropic_current_time_tool = {
    "name": "get_current_time",
    "description": "Get the current date and time for a timezone",
    "input_schema": {
        "type": "object",
        "properties": {"timezone": {"type": "string", "description": "timezone name"}},
        "required": ["timezone"],
    },
}
