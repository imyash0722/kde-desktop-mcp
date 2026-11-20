"""
Screenshot capture engine for KDE Plasma (Spectacle + ScreenShot2 + fallback).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional

from kde_desktop_mcp.windows import activate_kwin_window, get_kwin_windows


def default_screenshot_path(prefix: str = "kde_shot") -> str:
    """Generate a clean timestamped screenshot path."""
    out_dir = os.environ.get("XDG_RUNTIME_DIR", tempfile.gettempdir())
    ts = int(time.time() * 1000)
    return os.path.join(out_dir, f"{prefix}-{ts}.png")


def get_image_dimensions(path: str) -> Optional[List[int]]:
    """Return [width, height] of an image file."""
    try:
        from PIL import Image

        with Image.open(path) as img:
            return [img.width, img.height]
    except Exception:
        return None


def take_screenshot(
    window: Optional[str] = None,
    region: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Capture a screenshot of fullscreen, a specific window, or a rectangular region.

    Args:
        window: 'active', a window title/class substring, or a KWin window ID.
        region: Crop geometry in 'x,y,w,h' or 'x,y wxh' format.
        output_path: Absolute destination path for the PNG.

    Returns:
        Structured result dict with ok, target, path, dimensions, and backend.
    """
    dest = output_path or default_screenshot_path("kde_shot")
    dest_dir = os.path.dirname(os.path.abspath(dest))
    os.makedirs(dest_dir, exist_ok=True)

    spectacle_bin = shutil.which("spectacle")
    grim_bin = shutil.which("grim")

    # 1. Target is a window
    if window:
        target = window.strip()
        if target.lower() != "active":
            activate_kwin_window(target)
            time.sleep(0.15)

        if spectacle_bin:
            # -b: background mode, -n: non-notifying, -a: active window, -o: output
            cmd = [spectacle_bin, "-b", "-n", "-a", "-o", dest]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0:
                dims = get_image_dimensions(dest)
                return {
                    "ok": True,
                    "target": "window",
                    "window": target,
                    "path": dest,
                    "dimensions": dims,
                    "backend": "spectacle -a",
                }

        # Fallback to geometry query + grim
        windows = get_kwin_windows()
        matching = [
            w for w in windows
            if target.lower() in (w["title"] + " " + w["class"]).lower() or target == w["id"]
        ]
        if matching and grim_bin:
            win = matching[0]
            f_x, f_y, f_w, f_h = win["geometry"]
            cmd = [grim_bin, "-g", f"{f_x},{f_y} {f_w}x{f_h}", dest]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(dest):
                dims = get_image_dimensions(dest)
                return {
                    "ok": True,
                    "target": "window",
                    "window": win["title"],
                    "path": dest,
                    "geometry": [f_x, f_y, f_w, f_h],
                    "dimensions": dims,
                    "backend": "grim",
                }

    # 2. Target is a region
    if region:
        r = region.replace(" ", ",")
        parts = [int(p) for p in r.split(",") if p.strip()]
        if len(parts) == 4 and grim_bin:
            cmd = [grim_bin, "-g", f"{parts[0]},{parts[1]} {parts[2]}x{parts[3]}", dest]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(dest):
                dims = get_image_dimensions(dest)
                return {
                    "ok": True,
                    "target": "region",
                    "region": parts,
                    "path": dest,
                    "dimensions": dims,
                    "backend": "grim",
                }

    # 3. Fullscreen capture
    if spectacle_bin:
        cmd = [spectacle_bin, "-b", "-n", "-f", "-o", dest]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0:
            dims = get_image_dimensions(dest)
            return {
                "ok": True,
                "target": "fullscreen",
                "path": dest,
                "dimensions": dims,
                "backend": "spectacle -f",
            }

    # Fullscreen fallback to grim
    if grim_bin:
        cmd = [grim_bin, dest]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(dest):
            dims = get_image_dimensions(dest)
            return {
                "ok": True,
                "target": "fullscreen",
                "path": dest,
                "dimensions": dims,
                "backend": "grim",
            }

    return {
        "ok": False,
        "error": "Failed to capture screenshot. Neither spectacle nor grim produced an image.",
    }
