# get_weather tool func definition
from mcp_client import MCPClient
from mcp_manager import MCPManager
from typing import Optional, Any
import asyncio

BLUE = "\033[38;5;117m"
RESET = "\033[0m"


def execute_tool(self, tool_name: str, arguments: Optional[dict[str, Any]], mcpclient):
    """Overloading the async mpc client execute_tools() method"""
    execute_tool_coroutine = mcpclient.execute_tool(tool_name, arguments)
    future = asyncio.run_coroutine_threadsafe(execute_tool_coroutine, self.loop)
    return future.result()


print(f"{BLUE}--- From farewell tool definition ---{RESET}")

# Instantiate MCP client
mclient = MCPClient()

# Instantiate MCP manager with MCP client
print(f"{BLUE}Instantiating MCP Manager from farewell Tool{RESET}")
mManager = MCPManager("mcp manager", mclient)

mcp_server_path = "./mcptools/greetings/server.py"
result = mManager.start(mcp_server_path)

# define get_farewell
get_farewell = mManager.execute_tool
# get_farewell = execute_tool

# farewell tool config definition for google
google_farewell_tool = {
    "name": "farewell",
    "description": "farewell from MCP server",
    "parameters": {
        "type": "object",
        "properties": {"user": {"type": "string", "description": "user to farewell"}},
        "required": ["user"],
    },
}
