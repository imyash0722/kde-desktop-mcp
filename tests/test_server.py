"""Test server initialization and MCP tool registration."""

import asyncio
from kde_desktop_mcp.server import create_server


def test_server_creation():
    server = create_server()
    assert server is not None
    assert server.name == "kde-desktop-mcp"


def test_server_registered_tools():
    server = create_server()
    
    async def get_tool_names():
        tools = await server.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(get_tool_names())
    expected_tools = ["screenshot", "list_windows", "focus_window", "pointer", "type_text", "manage_daemon"]
    for t in expected_tools:
        assert t in tool_names, f"Expected tool '{t}' not registered in server"
