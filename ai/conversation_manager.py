"""Conversation history persistence for HI ROLEX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConversationManager:
    """Stores chat messages and saves them to data/conversation_history.json."""

    def __init__(self, history_path: Path | None = None) -> None:
        self.history_path = history_path or self._default_history_path()
        self.messages: list[dict[str, str]] = []
        self.load_history()

    def add_message(self, role: str, content: str) -> None:
        """Add one chat message to the runtime history."""
        self.messages.append({"role": role, "content": content})
        self.save_history()

    def get_history(self) -> list[dict[str, str]]:
        """Return a copy of the current conversation history."""
        return [message.copy() for message in self.messages]

    def clear_history(self) -> None:
        """Clear runtime and saved conversation history."""
        self.messages.clear()
        self.save_history()

    def save_history(self) -> None:
        """Save conversation history to disk."""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            self.history_path.write_text(
                json.dumps(self.messages, indent=4),
                encoding="utf-8",
            )
        except OSError:
            return

    def load_history(self) -> None:
        """Load conversation history without crashing on missing or invalid JSON."""
        if not self.history_path.exists():
            self.messages = []
            self.save_history()
            return

        try:
            loaded_data: Any = json.loads(self.history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.messages = []
            self.save_history()
            return

        if not isinstance(loaded_data, list):
            self.messages = []
            self.save_history()
            return

        self.messages = [
            {
                "role": str(message.get("role", "")),
                "content": str(message.get("content", "")),
            }
            for message in loaded_data
            if isinstance(message, dict)
        ]

    def _default_history_path(self) -> Path:
        """Return the default project conversation-history path."""
        return Path(__file__).resolve().parents[1] / "data" / "conversation_history.json"
