from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_time(timezone: str):
    return datetime.now(ZoneInfo(timezone))


current_time_tool = {
    "name": "get_current_time",
    "description": "Get the current date and time for a timezone",
    "parameters": {
        "type": "object",
        "properties": {"timezone": {"type": "string", "description": "timezone name"}},
        "required": ["timezone"],
    },
}
