"""Runtime command history for HI ROLEX automation."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class CommandHistory:
    """Stores automation commands during the current app session."""

    def __init__(self) -> None:
        self._commands: list[dict[str, Any]] = []

    def add_command(
        self,
        command: str,
        source: str = "automation",
        planned_actions: list[str] | None = None,
        success: bool | None = None,
    ) -> None:
        """Add a command to runtime history."""
        self._commands.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "command": command,
                "source": source,
                "planned_actions": planned_actions or [],
                "success": success,
            }
        )

    def clear_history(self) -> None:
        """Clear all stored runtime commands."""
        self._commands.clear()

    def get_history(self) -> list[dict[str, Any]]:
        """Return a copy of the current command history."""
        return [command.copy() for command in self._commands]
