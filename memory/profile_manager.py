"""User profile memory for HI ROLEX."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from memory.memory_manager import MemoryManager


class ProfileManager:
    """Stores simple user profile preferences in SQLite."""

    def __init__(self, database_path: Path | None = None) -> None:
        self.memory_manager = MemoryManager(database_path)

    def set_profile_value(self, key: str, value: str) -> bool:
        """Set one profile value when it is safe to store."""
        if not self.memory_manager.is_safe_to_store(f"{key} {value}"):
            return False

        try:
            with self.memory_manager._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO profile (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (key.strip(), value.strip()),
                )
            return True
        except sqlite3.Error:
            return False

    def get_profile_value(self, key: str) -> str | None:
        """Return one profile value."""
        try:
            with self.memory_manager._connect() as connection:
                row = connection.execute(
                    "SELECT value FROM profile WHERE key = ?",
                    (key.strip(),),
                ).fetchone()
            return str(row["value"]) if row else None
        except sqlite3.Error:
            return None

    def get_profile(self) -> dict[str, str]:
        """Return the full user profile."""
        try:
            with self.memory_manager._connect() as connection:
                rows = connection.execute("SELECT key, value FROM profile").fetchall()
            return {str(row["key"]): str(row["value"]) for row in rows}
        except sqlite3.Error:
            return {}
