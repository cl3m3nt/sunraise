import asyncio
from mcpclient import MCPClient
from threading import Thread
from typing import Any, Optional
import argparse


class MCPManager:

    def __init__(self, name: str, mcpclient: MCPClient):
        self.name = name
        self.mcpclient = mcpclient
        self.loop = None
        self.thread = None
        self.run_handle = None

    def _run_loop(self):
        """Helper function to make sure event loop run in background thread of MCP client process"""
        # Executing in the background thread
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self, server_script_path):
        """Start the MCP session by calling mcpclient.run()"""
        # creating the event loop (aka async scheduler) from asyncio
        self.loop = asyncio.new_event_loop()

        # defining coroutine from async connect_to_server function to be run within event loop
        run_coroutine = self.mcpclient.run(server_script_path)

        # Create the background thread
        self.thread = Thread(
            target=self._run_loop,  # to make sure event loop is attached to background thread
            daemon=True,
        )
        # Start the thread
        self.thread.start()

        #  Running the coroutine within the background thread of event loop
        self.run_handle = asyncio.run_coroutine_threadsafe(run_coroutine, self.loop)

        while not (
            self.mcpclient.started_event and self.mcpclient.started_event.is_set()
        ):
            pass

        # return self.run_handle.result()

    def get_tools(self):
        """Overloading the async mcp client get_tool() method"""
        get_tools_coroutine = self.mcpclient.get_tools()
        #  Running the coroutine within the background thread of event loop
        future = asyncio.run_coroutine_threadsafe(get_tools_coroutine, self.loop)

        return future.result()

    def execute_tool(self, tool_name: str, arguments: Optional[dict[str, Any]]):
        """Overloading the async mpc client execute_tools() method"""
        execute_tool_coroutine = self.mcpclient.execute_tool(tool_name, arguments)
        future = asyncio.run_coroutine_threadsafe(execute_tool_coroutine, self.loop)
        return future.result()

    def stop(self):
        """Stop the MCP session by updating shutdown_event state"""
        # Signal run() to exit its wait, then close the MCP session
        self.loop.call_soon_threadsafe(self.mcpclient.shutdown_event.set)

        # Wait for run() to finish (includes close()) before stopping the loop,
        # otherwise the stdio session/subprocess can be left unclosed.
        self.run_handle.result()

        # Stop the event loop and join the background thread
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        self.loop.close()
        print("--- Cleanly stopped everything ---")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Agent app")
    parser.add_argument(
        "--mcpserver",
        type=str,
        help="mcpserver name",
        choices=["greetings", "arithm", "calendar"],
        default="greetings",
    )
    args = parser.parse_args()
    mcpserver = args.mcpserver

    # MCP client with only exit_stack defined - mcp server and tools not instantiated yet
    print("--- Creating mcp client and mcp manager ---")
    mclient = MCPClient()

    # MCP manager with MCP client and no loop yet
    mManager = MCPManager("mcp manager", mclient)

    # Create an event loop in background thread with MCP manager start method
    # Launch the MCP server distinct process by asynchronously calling connect_to_server()

    if mcpserver == "greetings":
        mcp_server_path = "./mcptools/greetings/server.py"
    elif mcpserver == "arithm":
        mcp_server_path = "./mcptools/arithm/server.py"
    elif mcpserver == "calendar":
        mcp_server_path = "./mcptools/calendar/server.py"

    result = mManager.start(mcp_server_path)
    print(result)

    # Executing get_tools fom MCPManager
    tool_result = mManager.get_tools()
    print(tool_result)

    # ---------------------------------------------------------------------------
    # MCP GREETINGS SERVER
    # ---------------------------------------------------------------------------
    if mcpserver == "greetings":
        # execute_tools for greetings tool fom MCPManager
        greetings_tool_name = "greetings"
        greetings_tool_result = mManager.execute_tool(
            greetings_tool_name, {"user": "sunraise"}
        )
        print(greetings_tool_result)

        # execute_tools for multiply tool fom MCPManager
        farewell_tool_name = "farewell"
        farewell_tool_result = mManager.execute_tool(
            farewell_tool_name, {"user": "sunraise"}
        )
        print(farewell_tool_result)

    # ---------------------------------------------------------------------------
    # MCP ARITHM SERVER
    # ---------------------------------------------------------------------------
    elif mcpserver == "arithm":
        # execute_tools for add tool fom MCPManager
        add_tool_name = "add"
        arguments = {"a": 1, "b": 2}
        add_tool_result = mManager.execute_tool(add_tool_name, arguments)
        print(add_tool_result)

        # execute_tools for multiply tool fom MCPManager
        mult_tool_name = "multiply"
        arguments = {"a": 2, "b": 3}
        mult_tool_result = mManager.execute_tool(mult_tool_name, arguments)
        print(mult_tool_result)

    # ---------------------------------------------------------------------------
    # MCP CALENDAR SERVER
    # ---------------------------------------------------------------------------
    elif mcpserver == "calendar":
        # execute_tool for get_calendar_event tool fom MCPManager
        calendar_tool_name = "get_calendar_events"
        calendar_tool_result = mManager.execute_tool(calendar_tool_name, None)
        print(calendar_tool_result)

    mManager.stop()
