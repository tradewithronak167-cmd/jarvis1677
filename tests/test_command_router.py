"""Command router tests for HI ROLEX."""

from assistant.command_router import CommandRouter


def test_open_chrome_requires_confirmation() -> None:
    """Open Chrome should ask for confirmation before launching."""
    result = CommandRouter().handle_user_input("open chrome")

    assert result.confirmation_required
    assert "Confirmation required" in result.message


def test_unknown_open_app_requires_confirmation() -> None:
    """Installed app discovery should confirm before launching unknown app names."""
    result = CommandRouter().handle_user_input("open whatsapp")

    assert result.confirmation_required
    assert "Confirmation required" in result.message


def test_close_system_app_requires_confirmation() -> None:
    """Closing a Windows system tool should be supported but confirmed first."""
    result = CommandRouter().handle_user_input("close task manager")

    assert result.confirmation_required
    assert "Confirmation required" in result.message


def test_close_unknown_app_requires_confirmation() -> None:
    """Closing a discovered app should route through confirmation."""
    result = CommandRouter().handle_user_input("close whatsapp")

    assert result.confirmation_required
    assert "Confirmation required" in result.message


def test_delete_file_requires_confirmation() -> None:
    """Delete file must not execute without confirmation."""
    result = CommandRouter().handle_user_input("delete file test.txt")

    assert result.confirmation_required
    assert "Confirmation required" in result.message


def test_dangerous_command_is_refused() -> None:
    """Dangerous operations are refused."""
    result = CommandRouter().handle_user_input("format drive")

    assert not result.success
    assert "cannot perform" in result.message
