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
