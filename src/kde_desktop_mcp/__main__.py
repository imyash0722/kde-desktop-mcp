"""CLI execution entrypoint for kde-desktop-mcp."""
import sys
from kde_desktop_mcp.server import main

if __name__ == "__main__":
    sys.exit(main())
