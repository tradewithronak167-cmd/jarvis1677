"""Tests for the Day 7 rule-based command parser."""

from automation.command_parser import CommandParser


def test_open_chrome_command() -> None:
    """Open Chrome command maps to application launch."""
    parsed = CommandParser().parse("open google chrome")

    assert parsed.action == "open_application"
    assert parsed.target == "chrome"


def test_google_search_command() -> None:
    """Google search command extracts query text."""
    parsed = CommandParser().parse("search google for Python programming")

    assert parsed.action == "google_search"
    assert parsed.target == "python programming"


def test_open_folder_command() -> None:
    """Known folder command maps to folder opening."""
    parsed = CommandParser().parse("open downloads")

    assert parsed.action == "open_folder"
    assert parsed.target == "downloads"


def test_close_application_command() -> None:
    """Close command maps to application closing."""
    parsed = CommandParser().parse("close notepad")

    assert parsed.action == "close_application"
    assert parsed.target == "notepad"


def test_open_device_manager_command() -> None:
    """Device Manager is available as a safe system-tool launcher."""
    parsed = CommandParser().parse("open device manager")

    assert parsed.action == "open_application"
    assert parsed.target == "device manager"


def test_create_folder_command() -> None:
    """Create folder command maps to file management."""
    parsed = CommandParser().parse("create folder Projects")

    assert parsed.action == "create_folder"
    assert parsed.target == "Projects"


def test_rename_file_command() -> None:
    """Rename file command captures source and destination."""
    parsed = CommandParser().parse("rename file report.txt to final_report.txt")

    assert parsed.action == "rename"
    assert parsed.target == "report.txt"
    assert parsed.destination == "final_report.txt"


def test_delete_file_requires_confirmation() -> None:
    """Delete commands are parsed as confirmation-required actions."""
    parsed = CommandParser().parse("delete file notes.txt")

    assert parsed.action == "delete_requires_confirmation"
    assert parsed.target == "notes.txt"
