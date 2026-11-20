# KDE Desktop MCP

Custom Model Context Protocol server for KDE Plasma window capturing, screenshots, and pointer control.

## Overview
Exposes desktop interaction utilities to AI agents via the MCP protocol.

## Tools
- `screenshot`: Take full screen or window captures.
- `list_windows`: Query open application windows and coordinates.
- `focus_window`: Activate a window by name or identifier.
- `pointer`: Mouse cursor positioning, clicks, and wheel scrolls.
- `type_text`: Keystroke emulation.

## Local Setup
```bash
uv tool install --force .
```
