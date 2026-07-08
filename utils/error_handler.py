"""Reusable error handling helpers for HI ROLEX."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from utils.logger import get_logger

T = TypeVar("T")


def format_error(error: Exception) -> str:
    """Convert technical exceptions into user-friendly messages."""
    text = str(error)
    error_name = error.__class__.__name__

    if error_name == "ModuleNotFoundError":
        missing = text.split("'")[1] if "'" in text else "a required package"
        if missing in {"pycaw", "comtypes"}:
            return "Volume control is unavailable because a required package is missing."
        if missing == "screen_brightness_control":
            return "Brightness control is unavailable because a required package is missing."
        if missing == "pyaudio":
            return "Microphone access is unavailable because PyAudio is missing."
        return "This feature is unavailable because a required package is missing."

    if "connection" in text.casefold() or "timeout" in text.casefold():
        return "The service did not respond. Please check that it is running."

    return "Something went wrong, but HI ROLEX recovered safely."


def safe_execute(
    action: Callable[[], T],
    fallback: T,
    context: str = "operation",
) -> T:
    """Run an action safely and return fallback on errors."""
    try:
        return action()
    except Exception as error:
        get_logger().error("%s failed: %s", context, format_error(error))
        return fallback


def show_user_friendly_error(error: Exception) -> str:
    """Format and log an error for GUI display."""
    message = format_error(error)
    get_logger().error(message)
    return message
