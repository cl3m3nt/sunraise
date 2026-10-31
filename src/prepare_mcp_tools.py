def prepare_mcp_google(mcp_tool_def: dict):
    """Prepare tool definition from MCP server for google"""
    if "required" in mcp_tool_def["input_schema"]:
        mcp_google_tool = {
            "name": mcp_tool_def["name"],
            "description": mcp_tool_def["description"],
            "parameters": {
                "type": mcp_tool_def["input_schema"]["type"],
                "properties": mcp_tool_def["input_schema"]["properties"],
                "required": mcp_tool_def["input_schema"]["required"],
            },
        }
    else:
        mcp_google_tool = {
            "name": mcp_tool_def["name"],
            "description": mcp_tool_def["description"],
            "parameters": {
                "type": mcp_tool_def["input_schema"]["type"],
                "properties": mcp_tool_def["input_schema"]["properties"],
                "required": [],
            },
        }

    return mcp_google_tool
