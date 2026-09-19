# get_weather tool func definition
from mcpclient import MCPClient
from mcpmanager import MCPManager
from typing import Optional, Any
import asyncio

BLUE = "\033[38;5;117m"
RESET = "\033[0m"


def execute_tool(self, tool_name: str, arguments: Optional[dict[str, Any]], mcpclient):
    """Overloading the async mpc client execute_tools() method"""
    execute_tool_coroutine = mcpclient.execute_tool(tool_name, arguments)
    future = asyncio.run_coroutine_threadsafe(execute_tool_coroutine, self.loop)
    return future.result()


print(f"{BLUE}--- From greetings tool definition ---{RESET}")

# Instantiate MCP client
mclient = MCPClient()

# Instantiate MCP manager with MCP client
print(f"{BLUE}Instantiating MCP Manager from greetings Tool{RESET}")
mManager = MCPManager("mcp manager", mclient)

mcp_server_path = "./mcptools/greetings/server.py"
result = mManager.start(mcp_server_path)

# define get_greetings
get_greetings = mManager.execute_tool
# get_greetings = execute_tool

# greetings tool config definition for google
google_greetings_tool = {
    "name": "greetings",
    "description": "Greetings from MCP server",
    "parameters": {
        "type": "object",
        "properties": {"user": {"type": "string", "description": "user to greet"}},
        "required": ["user"],
    },
}
