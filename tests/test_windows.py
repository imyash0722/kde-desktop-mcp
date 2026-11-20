"""Test window introspection and activation fallback logic."""

import sys
from unittest.mock import MagicMock
from kde_desktop_mcp.windows import activate_kwin_window, get_kwin_windows


def test_get_kwin_windows_fallback_empty():
    # In an environment where KWin is not running or module throws, returns safe empty list
    windows = get_kwin_windows()
    assert isinstance(windows, list)


def test_get_kwin_windows_with_mock():
    mock_kwin = MagicMock()
    mock_window = MagicMock()
    mock_window.id = 1234
    mock_window.pid = 9999
    mock_window.caption = "Test Window"
    mock_window.resource_class = "test-app"
    mock_window.frame.x = 10
    mock_window.frame.y = 20
    mock_window.frame.width = 800
    mock_window.frame.height = 600
    mock_window.active = True
    mock_window.normal = True
    mock_kwin.geometry.collect_windows.return_value = [mock_window]

    orig_module = sys.modules.get("kwin_mcp")
    try:
        sys.modules["kwin_mcp"] = mock_kwin
        sys.modules["kwin_mcp.geometry"] = mock_kwin.geometry
        windows = get_kwin_windows()
        assert len(windows) == 1
        assert windows[0]["title"] == "Test Window"
        assert windows[0]["geometry"] == [10, 20, 800, 600]
    finally:
        if orig_module is not None:
            sys.modules["kwin_mcp"] = orig_module
        else:
            sys.modules.pop("kwin_mcp", None)
            sys.modules.pop("kwin_mcp.geometry", None)


def test_activate_kwin_window_fallback():
    # If not running or target not found, returns False safely
    assert activate_kwin_window("NonExistentWindow9999") is False
