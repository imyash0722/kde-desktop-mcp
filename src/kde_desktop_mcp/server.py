"""
FastMCP Server implementation for KDE Desktop automation.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from mcp.server.mcpserver import MCPServer

from kde_desktop_mcp.input import pointer_action, type_action
from kde_desktop_mcp.screenshot import take_screenshot
from kde_desktop_mcp.windows import activate_kwin_window, get_kwin_windows


def create_server() -> MCPServer:
    """Build and configure the KDE Desktop MCPServer instance."""
    server = MCPServer("kde-desktop-mcp")

    @server.tool()
    def screenshot(
        window: Optional[str] = None,
        region: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """Capture a screenshot of the entire desktop, a specific window, or a rectangular region in KDE.

        Args:
            window: Target window ('active', a window title/class substring, or a KWin window ID). If omitted and region is omitted, captures fullscreen.
            region: Crop geometry in 'x,y,w,h' format.
            output_path: Absolute destination path for the PNG. Defaults to a temporary file.
        """
        res = take_screenshot(window=window, region=region, output_path=output_path)
        return json.dumps(res)

    @server.tool()
    def list_windows() -> str:
        """List all open desktop windows in KDE, including their IDs, titles, classes, and geometries."""
        windows = get_kwin_windows()
        if not windows:
            return json.dumps({
                "ok": True,
                "count": 0,
                "windows": [],
                "note": "No windows found or KWin D-Bus interface is not active on current session.",
            })
        return json.dumps({
            "ok": True,
            "count": len(windows),
            "windows": windows,
        }, indent=2)

    @server.tool()
    def focus_window(window: str) -> str:
        """Raise and focus a window by its title, class substring, or KWin internal ID."""
        ok = activate_kwin_window(window)
        if ok:
            return json.dumps({"ok": True, "target": window, "status": "focused"})
        return json.dumps({
            "ok": False,
            "target": window,
            "error": "Window not found or could not be focused.",
        })

    @server.tool()
    def pointer(
        action: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        double: bool = False,
        scroll_dy: int = 0,
        scroll_dx: int = 0,
    ) -> str:
        """Simulate mouse actions (click, double-click, move, scroll) using system uinput/ydotool.

        Args:
            action: 'click', 'move', or 'scroll'.
            x: Global logical X coordinate.
            y: Global logical Y coordinate.
            button: 'left', 'right', or 'middle'.
            double: Whether to perform a double click.
            scroll_dy: Vertical scroll amount (positive = down, negative = up).
            scroll_dx: Horizontal scroll amount.
        """
        res = pointer_action(
            action=action,
            x=x,
            y=y,
            button=button,
            double=double,
            scroll_dy=scroll_dy,
            scroll_dx=scroll_dx,
        )
        return json.dumps(res)

    @server.tool()
    def type_text(text: str) -> str:
        """Type text into the currently focused window using system input synthesis."""
        res = type_action(text=text)
        return json.dumps(res)

    return server


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the kde-desktop-mcp server CLI."""
    parser = argparse.ArgumentParser(
        prog="kde-desktop-mcp",
        description="Model Context Protocol server for KDE Plasma desktop automation.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport to use (default: stdio)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args(argv)
    server = create_server()
    server.run(transport=args.transport)
    return 0
