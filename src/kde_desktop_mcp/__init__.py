"""
KDE Desktop MCP - Model Context Protocol server for KDE Plasma.
"""

__version__ = "0.1.0"

from kde_desktop_mcp.server import create_server, main

__all__ = ["__version__", "create_server", "main"]
