import os
import sys
import asyncio
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

        print("\nConnected to server")
        await self.close()

    async def get_tools(self, server_script_path: str):
        # Define the DISTINCT server PROCESS
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=os.environ.copy(),
        )

        # Create the STDIO CHANNEL for client/server communication and launch subprocess
        stdio, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Create the MCP communication/session over STDIO channel
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        # Perform the MCP handshake between client/server to initialize session
        await self.session.initialize()

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
        await self.close()

    async def execute_tool(
        self,
        tool_name: str,
        server_script_path: str,
        arguments: Optional[dict[str, Any]] = None,
    ) -> str:
        if self.session is None:
            raise RuntimeError(
                "Client is not connected. Call connect_to_server() first."
            )

        # Init mcp server session
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

        result = await self.session.call_tool(tool_name, arguments or {})
        print(f"\nExecuted tool {tool_name} result:", result.structuredContent)

        await self.close()
        return self._result_to_text(result)

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


if __name__ == "__main__":
    m = MCPClient()

    mcp_server_path = "./server.py"

    coroutine_connect = m.connect_to_server(mcp_server_path)

    # connecting to MCP server
    print("--- mcp client/server connection ---")
    asyncio.run(coroutine_connect)

    # listing MCP tools of the MCP server
    print("--- mcp tools---")
    coroutine_get_tools = m.get_tools(mcp_server_path)
    mtools = asyncio.run(coroutine_get_tools)

    # Executing MCP tools of the MCP server
    print("--- addition tool ---")
    coroutine_execute_tools = m.execute_tool("add", mcp_server_path, {"a": 1, "b": 2})
    tool_result = asyncio.run(coroutine_execute_tools)
    print(tool_result)
