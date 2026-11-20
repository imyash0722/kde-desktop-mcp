"""Test screenshot module utilities and capture logic."""

import os
import tempfile
from unittest.mock import MagicMock, patch

from kde_desktop_mcp.screenshot import default_screenshot_path, get_image_dimensions, take_screenshot


def test_default_screenshot_path():
    p = default_screenshot_path("test_prefix")
    assert "test_prefix-" in os.path.basename(p)
    assert p.endswith(".png")


def test_get_image_dimensions_invalid_path():
    assert get_image_dimensions("/path/to/nonexistent/image.png") is None


@patch("shutil.which")
@patch("subprocess.run")
def test_take_screenshot_spectacle_fullscreen(mock_run, mock_which):
    mock_which.side_effect = lambda cmd: "/usr/bin/spectacle" if cmd == "spectacle" else None
    
    # Mock subprocess return
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_run.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".png") as tf:
        tf.write(b"fake image data")
        tf.flush()
        with patch("kde_desktop_mcp.screenshot.get_image_dimensions", return_value=[1920, 1080]):
            res = take_screenshot(output_path=tf.name)
            assert res["ok"] is True
            assert res["target"] == "fullscreen"
            assert res["backend"] == "spectacle -f"
            assert res["dimensions"] == [1920, 1080]


@patch("shutil.which")
def test_take_screenshot_no_backends(mock_which):
    mock_which.return_value = None
    res = take_screenshot()
    assert res["ok"] is False
    assert "Neither spectacle nor grim" in res["error"]
