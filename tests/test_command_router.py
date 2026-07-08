"""Command router tests for HI ROLEX."""

from assistant.command_router import CommandRouter


def test_open_chrome_creates_direct_action() -> None:
    """Open Chrome should be planned as a direct app action."""
    plan = CommandRouter().create_plan("open chrome")

    assert plan.actions[0].intent.category == "open_app"
    assert not plan.requires_confirmation


def test_unknown_open_app_creates_direct_action() -> None:
    """Installed app discovery should launch app names directly."""
    plan = CommandRouter().create_plan("open whatsapp")

    assert plan.actions[0].intent.category == "open_app"
    assert plan.actions[0].intent.target == "whatsapp"
    assert not plan.requires_confirmation


def test_close_system_app_creates_direct_action() -> None:
    """Closing a Windows system tool should be supported directly."""
    plan = CommandRouter().create_plan("close task manager")

    assert plan.actions[0].intent.category == "close_app"
    assert plan.actions[0].intent.target == "task manager"
    assert not plan.requires_confirmation


def test_close_unknown_app_creates_direct_action() -> None:
    """Closing a discovered app should route directly."""
    plan = CommandRouter().create_plan("close whatsapp")

    assert plan.actions[0].intent.category == "close_app"
    assert plan.actions[0].intent.target == "whatsapp"
    assert not plan.requires_confirmation


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
