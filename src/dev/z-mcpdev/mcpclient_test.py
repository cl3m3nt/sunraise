import asyncio
import os
import sys
from contextlib import AsyncExitStack
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools: list[dict[str, Any]] = []

    async def connect_to_server(self, server_script_path: str) -> None:
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py file")

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=os.environ.copy(),
        )

        stdio, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await self.session.initialize()
       
        msg = "\nConnected to server"
        print(msg)
        return msg

    async def get_tools(self, server_script_path: str):

        # Send the MCP msg 'list_tools()' over the MCP session and wait server response
        response = await self.session.list_tools()

        self.tools = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        print("\nConnected to server with tools:", [t["name"] for t in self.tools])

        return self.tools

    async def execute_tool(self, tool_name: str,server_script_path:str, arguments: Optional[dict[str, Any]] = None) -> str:
       
        response = await self.session.call_tool(tool_name, arguments or {})
        print(f"\nExecuted tool {tool_name} result:", response.structuredContent)
        
        return self._result_to_text(response)

    async def close(self) -> None:
        await self.exit_stack.aclose()

    @staticmethod
    def _result_to_text(result: Any) -> str:
        """Flatten an MCP tool result into plain text for the model."""
        parts: list[str] = []
        for block in getattr(result, "content", None) or []:
            text = getattr(block, "text", None)
            if text is not None:
                parts.append(str(text))
        return "\n".join(parts) if parts else str(result)


async def main():

    client = MCPClient()

    server_path = "/Users/clement/Desktop/sunraise/src/mcptools/arithm/server.py"

    try:
        print("--- connect ---")
        await client.connect_to_server(server_path)

        print("--- tools ---")
        tools = await client.get_tools(server_path)
        print(tools)

        print("--- execute ---")
        result = await client.execute_tool(
            "add",
            server_path,
            {"a": 1, "b": 2}
        )
        print(result)

    finally:
        print("--- closing ---")
        await client.close()


if __name__ == "__main__":
    asyncio.run(main()) # this expect the self.exit_stack.aclose() to finish properly the event loop