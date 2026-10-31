from mcp.server.fastmcp import FastMCP
from authentication import get_credentials, get_calendar
from datetime import datetime, timezone, timedelta

mcp = FastMCP("google-calendar")


@mcp.tool()
def get_calendar_events() -> dict:
    "Get calendar events"
    creds = get_credentials()

    now = datetime.now(timezone.utc)
    one_month_ago = now - timedelta(days=30)

    events = (
        get_calendar(creds)
        .events()
        .list(
            calendarId="primary",
            timeMin=one_month_ago.isoformat(),
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events


if __name__ == "__main__":

    mcp.run()
