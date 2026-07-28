import asyncio
import os
import sys
from contextlib import AsyncExitStack
from typing import Any, Optional
from waiting import get_waiting

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools: list[dict[str, Any]] = []
        self.started_event = None
        self.shutdown_event = None

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

        msg = "\n--- Connected to MCP server ---"
        print(msg)
        return msg

    async def run(self, server_script_path):
        self.started_event = asyncio.Event()
        self.shutdown_event = asyncio.Event()

        await self.connect_to_server(server_script_path)
        self.started_event.set()
        print("--- MCP session running ---")

        """
        while (self.shutdown_event.is_set() is not True):
            print("--- waiting for shutdown event ---")
            await asyncio.sleep(5) 
            # event loop can continue, only this coroutine is paused 5s
            # so this gives "illusion" that the session run lasts 5s more
        """

        await self.shutdown_event.wait()

        print("--- MCP session stopping ---")

        await self.close()

    async def get_tools(self):

        # Send the MCP primitive msg 'list_tools()' over the MCP session and wait server response
        response = await self.session.list_tools()

        self.tools = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        print(
            f"\n--- Connected to MCP server with tools: {[t["name"] for t in self.tools]} ---"
        )

        return self.tools

    async def execute_tool(
        self, tool_name: str, arguments: Optional[dict[str, Any]] = None
    ) -> str:

        # Emulating a need to wait 5 second to get information
        # like if there is a workflow to get and process info with the LLM

        if tool_name == "get_calendar_events":
            print("--- Getting calendar info ---")
            await asyncio.sleep(5)
            print("--- Finalizing calendar workflow ---")
            await asyncio.sleep(3)
            get_waiting()

        elif tool_name == "add":
            print(f"--- Adding  {arguments} ---")
            await asyncio.sleep(5)
            print("--- Finalizing addition workflow ---")
            await asyncio.sleep(3)
            get_waiting()

        elif tool_name == "multiply":
            print(f"--- Multiplying  {arguments} ---")
            await asyncio.sleep(5)
            print("--- Finalizing multiplication workflow ---")
            await asyncio.sleep(3)

            get_waiting()

        elif tool_name == "greetings":
            print(f"--- Greetings  {arguments} ---")
            await asyncio.sleep(5)
            print("--- Finalizing greetings workflow ---")
            await asyncio.sleep(3)

            get_waiting()

        elif tool_name == "farewell":
            print(f"--- Farewell  {arguments} ---")
            await asyncio.sleep(5)
            print("--- Finalizing farewell workflow ---")
            await asyncio.sleep(3)

            get_waiting()

        # Send the MCP primitive msg 'call_tool()' over the MCP session and wait server response
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
