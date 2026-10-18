import asyncio
from mcpclient import MCPClient
from threading import Thread
from typing import Any, Optional

class MCPManager:

    def __init__(self,name: str, mcpclient: MCPClient):
        self.name = name
        self.mcpclient = mcpclient
        self.loop = None
        self.thread = None

    def _run_loop(self):
        # Executing in the background thread
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self,server_script_path):
        # creating the event loop (aka async scheduler) from asyncio
        self.loop = asyncio.new_event_loop()

        # defining coroutine from async connect_to_server function to be run within event loop
        connect_to_server_coroutine = self.mcpclient.connect_to_server(server_script_path)

       # Create the background thread
        self.thread = Thread(
            target=self._run_loop, # to make sure event loop is attached to background thread
            daemon=True
        )
        # Start the thread
        self.thread.start()

        #  Running the coroutine within the background thread of event loop
        future = asyncio.run_coroutine_threadsafe(
            connect_to_server_coroutine,
            self.loop
            )

        return future.result()

    def get_tools(self):
        get_tools_coroutine = self.mcpclient.get_tools()
        #  Running the coroutine within the background thread of event loop
        future = asyncio.run_coroutine_threadsafe(
            get_tools_coroutine,
            self.loop
            )
        
        return future.result()
        
    
    def execute_tool(self, tool_name: str, arguments: Optional[dict[str, Any]]):
        execute_tool_coroutine = self.mcpclient.execute_tool(tool_name,arguments)
        future = asyncio.run_coroutine_threadsafe(
            execute_tool_coroutine,
            self.loop
        )
        return future.result()
    
    def stop(self):
        #Stopping MCP session by closing the async exit_stack
        stop_coroutine = self.mcpclient.close()
        future = asyncio.run_coroutine_threadsafe(
            stop_coroutine,
            self.loop
        )
        result = future.result() # wait for mcpclient to close()

         # stop event loop
        self.loop.call_soon_threadsafe(
        self.loop.stop
        )

        # wait for thread termination
        self.thread.join()

        # delete the event loop
        self.loop.close()

        return result


if __name__ == "__main__":
    # MCP client with only exit_stack defined - mcp server and tools not instantiated yet
    mclient = MCPClient()
    print(mclient.__dict__)

    # MCP manager with MCP client and no loop yet
    mManager = MCPManager("mcp manager", mclient)
    print(mManager.__dict__)

    # Create an event loop in background thread with MCP manager start method
    # Launch the MCP server distinct process by asynchronously calling connect_to_server()
    mcp_server_path = '/Users/clement/Desktop/sunraise/src/mcptools/arithm/server.py'
    result = mManager.start(mcp_server_path)
    print(result)
    print(mManager.mcpclient.session)

    # Executing get_tools fom MCPManager
    tool_result = mManager.get_tools()
    print(tool_result)

    # Executing execute_tools fom MCPManager
    add_tool_name = "add"
    arguments = {"a":1, "b":2}
    add_tool_result = mManager.execute_tool(add_tool_name,arguments)
    print(add_tool_result)

    # Executing execute_tools fom MCPManager
    mult_tool_name = "multiply"
    arguments = {"a":2, "b":3}
    mult_tool_result = mManager.execute_tool(mult_tool_name,arguments)
    print(mult_tool_result)

    # Stopping the async stack
    mManager.stop()

    