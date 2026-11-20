"""
KWin window introspection and activation via D-Bus scripting interface.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


def get_kwin_windows(timeout: float = 3.0) -> List[Dict[str, Any]]:
    """Query open windows from the KWin scripting interface.

    Returns:
        List of dicts with window metadata:
        [{'id': str, 'pid': int, 'title': str, 'class': str,
          'geometry': [x, y, w, h], 'active': bool, 'normal': bool}]
    """
    try:
        from kwin_mcp.geometry import collect_windows

        raw_windows = collect_windows(timeout=timeout)
        windows: List[Dict[str, Any]] = []
        for w in raw_windows:
            windows.append({
                "id": str(w.id),
                "pid": w.pid,
                "title": w.caption,
                "class": w.resource_class,
                "geometry": [w.frame.x, w.frame.y, w.frame.width, w.frame.height],
                "active": w.active,
                "normal": w.normal,
            })
        return windows
    except Exception:
        # KWin not running on current session bus or module unavailable
        return []


def activate_kwin_window(needle_or_id: str, timeout: float = 3.0) -> bool:
    """Activate a window by KWin internal ID or title/class substring.

    Args:
        needle_or_id: Title/class substring or exact internal ID.
        timeout: Timeout in seconds for KWin D-Bus roundtrip.

    Returns:
        True if window was activated, False otherwise.
    """
    try:
        from kwin_mcp.geometry import activate_window

        res = activate_window(needle=needle_or_id.lower().strip(), timeout=timeout)
        return bool(res)
    except Exception:
        return False
