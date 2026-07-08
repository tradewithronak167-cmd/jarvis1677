"""Tests for Windows application launcher helpers."""

from __future__ import annotations

from automation.app_launcher import AppLauncher


def test_notepad_has_available_launch_command() -> None:
    """Notepad should have at least one launch command on Windows."""
    launcher = AppLauncher()
    app = launcher.APPLICATIONS["notepad"]

    commands = launcher._candidate_commands("notepad", app)

    assert commands


def test_unsupported_application_returns_error() -> None:
    """Unknown app names should fail gracefully."""
    success, message = AppLauncher().open_application("missing-test-app")

    assert not success
    assert "not supported" in message


def test_system_tools_have_launch_commands() -> None:
    """Safe Windows system tools should be registered for chat launching."""
    launcher = AppLauncher()
    for app_name in ("task manager", "settings", "device manager", "system information"):
        app = launcher.APPLICATIONS[app_name]
        assert launcher._candidate_commands(app_name, app)
