from mcp.server.fastmcp import FastMCP
from authentication import get_credentials, get_calendar

mcp = FastMCP("mcp-google-calendar")


@mcp.tool()
def get_calendar_events() -> dict:
    creds = get_credentials()
    events = (
        get_calendar(creds)
        .events()
        .list(
            calendarId="primary", maxResults=20, singleEvents=True, orderBy="startTime"
        )
        .execute()
    )
    return events


if __name__ == "__main__":

    mcp.run()
