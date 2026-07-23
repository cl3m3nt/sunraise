from mcp.server.fastmcp import FastMCP

mcp = FastMCP("greetings")


@mcp.tool()
def greetings(user: str) -> str:
    "Greet a user"
    return f"Greetings {user}!"


@mcp.tool()
def farewell(user: str) -> str:
    "Farewell a user"
    return f"Farewell {user}!"


if __name__ == "__main__":

    mcp.run()
