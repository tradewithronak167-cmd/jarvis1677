"""Command router tests for HI ROLEX."""

from assistant.command_router import CommandRouter


def test_open_chrome_creates_safe_action() -> None:
    """Open Chrome is planned as a safe action."""
    plan = CommandRouter().create_plan("open chrome")

    assert plan.actions[0].intent.category == "open_app"
    assert not plan.requires_confirmation


def test_unknown_open_app_creates_launch_action() -> None:
    """Installed app discovery should handle app names beyond the fixed alias list."""
    plan = CommandRouter().create_plan("open whatsapp")

    assert plan.actions[0].intent.category == "open_app"
    assert plan.actions[0].intent.target == "whatsapp"


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
