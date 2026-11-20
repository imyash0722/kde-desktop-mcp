"""
Input automation engine for mouse and keyboard simulation.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Any, Dict, Optional


def pointer_action(
    action: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left",
    double: bool = False,
    scroll_dy: int = 0,
    scroll_dx: int = 0,
) -> Dict[str, Any]:
    """Execute pointer actions (click, move, scroll) via ydotool.

    Args:
        action: 'click', 'move', or 'scroll'.
        x: Global logical X coordinate.
        y: Global logical Y coordinate.
        button: 'left', 'right', or 'middle'.
        double: Whether to perform a double click.
        scroll_dy: Vertical scroll amount (positive = down, negative = up).
        scroll_dx: Horizontal scroll amount.

    Returns:
        Status dictionary with operation details.
    """
    ydotool = shutil.which("ydotool")
    if not ydotool:
        return {"ok": False, "error": "ydotool is not installed on this system."}

    action_norm = action.lower().strip()

    # Move cursor first if coordinates provided
    if x is not None and y is not None:
        try:
            subprocess.run(
                [ydotool, "mousemove", "-a", "-x", str(x), "-y", str(y)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Failed to move pointer to ({x}, {y}): {e}"}

    if action_norm == "move":
        return {"ok": True, "action": "move", "position": [x, y]}

    if action_norm == "click":
        button_map = {
            "left": "0xC0",
            "right": "0xC1",
            "middle": "0xC2",
        }
        btn_code = button_map.get(button.lower(), "0xC0")
        click_cmd = [ydotool, "click", btn_code]
        if double:
            click_cmd.extend(["-r", "2", "-D", "50"])
        try:
            subprocess.run(click_cmd, check=True, capture_output=True)
            return {
                "ok": True,
                "action": "click",
                "button": button,
                "double": double,
                "at": [x, y],
            }
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Failed to click button {button}: {e}"}

    if action_norm == "scroll":
        # ydotool mousemove -w requires both -x and -y
        scroll_cmd = [ydotool, "mousemove", "-w", "-x", str(scroll_dx), "-y", str(scroll_dy)]
        try:
            subprocess.run(scroll_cmd, check=True, capture_output=True)
            return {
                "ok": True,
                "action": "scroll",
                "delta_y": scroll_dy,
                "delta_x": scroll_dx,
                "at": [x, y],
            }
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Failed to scroll: {e}"}

    return {"ok": False, "error": f"Unknown pointer action: {action}"}


def type_action(text: str) -> Dict[str, Any]:
    """Type arbitrary text into the currently focused window."""
    wtype = shutil.which("wtype")
    ydotool = shutil.which("ydotool")

    if wtype:
        try:
            subprocess.run([wtype, "--", text], check=True, capture_output=True)
            return {"ok": True, "typed": text, "backend": "wtype"}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"wtype typing failed: {e}"}
    elif ydotool:
        try:
            subprocess.run([ydotool, "type", "--", text], check=True, capture_output=True)
            return {"ok": True, "typed": text, "backend": "ydotool"}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"ydotool typing failed: {e}"}

    return {"ok": False, "error": "Neither wtype nor ydotool is available for typing."}


def manage_ydotool_daemon(action: str = "status") -> Dict[str, Any]:
    """Check, start, stop, or restart the ydotool daemon.

    Uses systemd user service ('systemctl --user') with fallback to direct process management.
    """
    action_norm = action.lower().strip()
    systemctl = shutil.which("systemctl")

    if action_norm == "status":
        is_active = False
        details = ""
        if systemctl:
            res = subprocess.run(
                [systemctl, "--user", "is-active", "ydotool.service"],
                capture_output=True,
                text=True,
            )
            is_active = res.stdout.strip() == "active"
            details = res.stdout.strip()
        if not is_active:
            pgrep = shutil.which("pgrep")
            if pgrep:
                res = subprocess.run([pgrep, "-x", "ydotoold"], capture_output=True, text=True)
                if res.returncode == 0:
                    is_active = True
                    details = f"running (pid {res.stdout.strip()})"
        return {"ok": True, "active": is_active, "status": details or "inactive"}

    if action_norm == "start":
        if systemctl:
            res = subprocess.run(
                [systemctl, "--user", "start", "ydotool.service"],
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                return {"ok": True, "action": "start", "status": "started via systemd --user"}
        ydotoold = shutil.which("ydotoold")
        if ydotoold:
            subprocess.Popen([ydotoold], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"ok": True, "action": "start", "status": "started background process"}
        return {"ok": False, "error": "Failed to start ydotoold: neither systemd service nor binary found."}

    if action_norm == "stop":
        if systemctl:
            res = subprocess.run(
                [systemctl, "--user", "stop", "ydotool.service"],
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                return {"ok": True, "action": "stop", "status": "stopped via systemd --user"}
        pkill = shutil.which("pkill")
        if pkill:
            subprocess.run([pkill, "-x", "ydotoold"], capture_output=True)
            return {"ok": True, "action": "stop", "status": "killed ydotoold process"}
        return {"ok": False, "error": "Could not stop ydotoold."}

    if action_norm == "restart":
        if systemctl:
            res = subprocess.run(
                [systemctl, "--user", "restart", "ydotool.service"],
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                return {"ok": True, "action": "restart", "status": "restarted via systemd --user"}
        manage_ydotool_daemon("stop")
        return manage_ydotool_daemon("start")

    return {
        "ok": False,
        "error": f"Unknown daemon action: {action}. Use 'status', 'start', 'stop', or 'restart'.",
    }
