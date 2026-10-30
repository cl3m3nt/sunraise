from mcp.server.fastmcp import FastMCP

mcp = FastMCP("greetings")


@mcp.tool()
def greetings(user: str) -> str:
    "Greet a user"
    return f"Greetings {user} c'est génial de faire ta connaissance!"


@mcp.tool()
def farewell(user: str) -> str:
    "Farewell a user"
    return f"Farewell {user}, c'est dommage de te dire au revoir!"


if __name__ == "__main__":

    mcp.run()
