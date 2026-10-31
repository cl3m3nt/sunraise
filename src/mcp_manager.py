import asyncio
import logging
from mcp_client import MCPClient
from threading import Thread
from typing import Any, Optional

# Logger config
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class MCPManager:

    def __init__(self, name: str, mcp_client: MCPClient):
        self.name = name
        self.mcp_client = mcp_client
        self.loop = None
        self.thread = None
        self.run_handle = None

    def _run_loop(self):
        """Helper function to make sure event loop run in background thread of MCP client process"""
        # Executing in the background thread
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self, server_script_path):
        """Start the MCP session by calling mcp_client.run()"""
        # creating the event loop (aka async scheduler) from asyncio
        self.loop = asyncio.new_event_loop()

        # defining coroutine from async connect_to_server function to be run within event loop
        # print("From MCP manager: launching MCP session from MCP client:")
        run_coroutine = self.mcp_client.run(server_script_path)

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
            self.mcp_client.started_event and self.mcp_client.started_event.is_set()
        ):
            pass

        # return self.run_handle.result()

    def get_tools(self):
        """Overloading the async mcp client get_tool() method"""
        logger.info("From MCP manager: getting MCP tools")
        get_tools_coroutine = self.mcp_client.get_tools()
        #  Running the coroutine within the background thread of event loop
        future = asyncio.run_coroutine_threadsafe(get_tools_coroutine, self.loop)

        return future.result()

    def execute_tool(self, tool_name: str, arguments: Optional[dict[str, Any]]):
        """Overloading the async mpc client execute_tools() method"""
        execute_tool_coroutine = self.mcp_client.execute_tool(tool_name, arguments)
        future = asyncio.run_coroutine_threadsafe(execute_tool_coroutine, self.loop)
        return future.result()

    def stop(self):
        """Stop the MCP session by updating shutdown_event state"""
        # Signal run() to exit its wait, then close the MCP session
        self.loop.call_soon_threadsafe(self.mcp_client.shutdown_event.set)

        # Wait for run() to finish (includes close()) before stopping the loop,
        # otherwise the stdio session/subprocess can be left unclosed.
        self.run_handle.result()

        # Stop the event loop and join the background thread
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        self.loop.close()
        print("--- Cleanly stopped everything ---")
