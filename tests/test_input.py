"""Test mouse and keyboard input automation."""

from unittest.mock import patch
from kde_desktop_mcp.input import pointer_action, type_action


@patch("shutil.which")
@patch("subprocess.run")
def test_pointer_action_move(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/ydotool"
    res = pointer_action(action="move", x=250, y=350)
    assert res["ok"] is True
    assert res["action"] == "move"
    assert res["position"] == [250, 350]


@patch("shutil.which")
@patch("subprocess.run")
def test_pointer_action_click(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/ydotool"
    res = pointer_action(action="click", x=100, y=200, button="right", double=True)
    assert res["ok"] is True
    assert res["action"] == "click"
    assert res["button"] == "right"
    assert res["double"] is True
    assert res["at"] == [100, 200]


@patch("shutil.which")
@patch("subprocess.run")
def test_pointer_action_scroll(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/ydotool"
    res = pointer_action(action="scroll", x=500, y=500, scroll_dy=3, scroll_dx=-1)
    assert res["ok"] is True
    assert res["action"] == "scroll"
    assert res["delta_y"] == 3
    assert res["delta_x"] == -1


def test_pointer_action_unknown():
    with patch("shutil.which", return_value="/usr/bin/ydotool"):
        res = pointer_action(action="invalid_action")
        assert res["ok"] is False
        assert "Unknown pointer action" in res["error"]


@patch("shutil.which")
@patch("subprocess.run")
def test_type_action(mock_run, mock_which):
    mock_which.side_effect = lambda cmd: "/usr/bin/wtype" if cmd == "wtype" else None
    res = type_action("hello world")
    assert res["ok"] is True
    assert res["typed"] == "hello world"
    assert res["backend"] == "wtype"
