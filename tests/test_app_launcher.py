"""Tests for Windows application launcher helpers."""

from __future__ import annotations

import os
from pathlib import Path

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
    assert "could not find" in message.casefold()


def test_system_tools_have_launch_commands() -> None:
    """Safe Windows system tools should be registered for chat launching."""
    launcher = AppLauncher()
    for app_name in (
        "task manager",
        "settings",
        "device manager",
        "system information",
        "resource monitor",
        "performance monitor",
        "event viewer",
    ):
        app = launcher.APPLICATIONS[app_name]
        assert launcher._candidate_commands(app_name, app)


def test_system_tools_have_close_process_names() -> None:
    """Safe Windows system tools should also define close targets."""
    launcher = AppLauncher()
    for app_name in (
        "task manager",
        "settings",
        "control panel",
        "device manager",
        "system information",
        "resource monitor",
        "performance monitor",
        "event viewer",
    ):
        assert launcher.APPLICATIONS[app_name].process_names


def test_generic_start_menu_app_can_launch(monkeypatch, tmp_path: Path) -> None:
    """Unknown app names should be opened when a Start Menu shortcut exists."""
    shortcut = tmp_path / "Example App.lnk"
    shortcut.write_text("", encoding="utf-8")
    opened_paths: list[Path] = []
    launcher = AppLauncher()

    monkeypatch.setattr(launcher, "_start_menu_shortcuts", lambda: [shortcut])
    monkeypatch.setattr(os, "startfile", lambda path: opened_paths.append(Path(path)))

    success, message = launcher.open_application("example app")

    assert success
    assert opened_paths == [shortcut]
    assert "Launch requested" in message
