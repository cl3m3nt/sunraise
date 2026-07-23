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

    async def execute_tool(
        self, tool_name: str, arguments: Optional[dict[str, Any]] = None
    ) -> str:
        if self.session is None:
            raise RuntimeError(
                "Client is not connected. Call connect_to_server() first."
            )

        result = await self.session.call_tool(tool_name, arguments or {})
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

    async def main() -> None:
        print("--- creating mcp client ---")
        m = MCPClient()
        try:
            await m.connect_to_server("./server.py")
            print("--- greetings ---")
            tool_result = await m.execute_tool("greetings", {"user": "john doe"})
            print("\nTool result:\n", tool_result)
            print("--- farewell ---")
            tool_result = await m.execute_tool("farewell", {"user": "john doe"})
            print("\nTool result:\n", tool_result)

        finally:
            await m.close()

    asyncio.run(main())
