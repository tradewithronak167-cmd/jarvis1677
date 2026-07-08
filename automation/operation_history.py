"""Persistent file-operation history for HI ROLEX."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

from utils.app_paths import DATA_DIR


class OperationHistory:
    """Stores file operation history in data/file_history.json."""

    def __init__(self, history_path: Path | None = None) -> None:
        self.history_path = history_path or self._default_path("file_history.json")

    def add_operation(self, operation: str, result: str = "") -> None:
        """Add a file operation record to history."""
        history = self.get_history()
        history.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "operation": operation,
                "result": result,
            }
        )
        self._save_history(history)

    def get_history(self) -> list[dict[str, str]]:
        """Return saved file operation history."""
        if not self.history_path.exists():
            self._save_history([])
            return []

        try:
            data: Any = json.loads(self.history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._save_history([])
            return []

        if not isinstance(data, list):
            self._save_history([])
            return []

        return [
            {
                "timestamp": str(item.get("timestamp", "")),
                "operation": str(item.get("operation", "")),
                "result": str(item.get("result", "")),
            }
            for item in data
            if isinstance(item, dict)
        ]

    def clear_history(self) -> None:
        """Clear all stored file operation history."""
        self._save_history([])

    def _save_history(self, history: list[dict[str, str]]) -> None:
        """Write history to disk."""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(json.dumps(history, indent=4), encoding="utf-8")

    def _default_path(self, filename: str) -> Path:
        """Return a project data path."""
        return DATA_DIR / filename
