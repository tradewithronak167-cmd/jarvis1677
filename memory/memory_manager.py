"""Safe local SQLite memory manager for HI ROLEX."""

from __future__ import annotations

from pathlib import Path
import re
import sqlite3

from memory.memory_models import MemoryRecord
from utils.app_paths import MEMORY_DB_PATH
from utils.logger import get_logger
from utils.validators import is_sensitive_text


class MemoryManager:
    """Stores and retrieves safe long-term memories."""

    SENSITIVE_PATTERNS: tuple[str, ...] = (
        "password",
        "api key",
        "apikey",
        "access token",
        "token",
        "pin",
        "bank",
        "card number",
        "credit card",
        "debit card",
        "cvv",
        "otp",
        "private key",
        "secret key",
        "seed phrase",
    )

    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or self._default_database_path()
        self.logger = get_logger()
        self.initialize_database()

    def initialize_database(self) -> None:
        """Create memory tables when the database does not exist."""
        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS profile (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        summary TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        except sqlite3.Error as error:
            self.logger.error("Memory database initialization failed: %s", error)
            return

    def add_memory(self, category: str, key: str, value: str) -> bool:
        """Add a safe long-term memory."""
        if not self.is_safe_to_store(f"{category} {key} {value}"):
            return False

        try:
            with self._connect() as connection:
                connection.execute(
                    "INSERT INTO memories (category, key, value) VALUES (?, ?, ?)",
                    (category.strip(), key.strip(), value.strip()),
                )
            return True
        except sqlite3.Error as error:
            self.logger.error("Add memory failed: %s", error)
            return False

    def get_memory(self, key: str) -> str | None:
        """Return the newest memory value for a key."""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT value FROM memories
                    WHERE key = ?
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (key.strip(),),
                ).fetchone()
            return str(row["value"]) if row else None
        except sqlite3.Error:
            return None

    def get_all_memories(self) -> list[MemoryRecord]:
        """Return all saved long-term memories."""
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT id, category, key, value, created_at
                    FROM memories
                    ORDER BY id DESC
                    """
                ).fetchall()
            return [self._row_to_memory(row) for row in rows]
        except sqlite3.Error:
            return []

    def search_memories(self, query: str) -> list[MemoryRecord]:
        """Search memories by category, key, or value."""
        like_query = f"%{query.strip()}%"
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT id, category, key, value, created_at
                    FROM memories
                    WHERE category LIKE ? OR key LIKE ? OR value LIKE ?
                    ORDER BY id DESC
                    """,
                    (like_query, like_query, like_query),
                ).fetchall()
            return [self._row_to_memory(row) for row in rows]
        except sqlite3.Error:
            return []

    def delete_memory(self, memory_id: int) -> bool:
        """Delete one memory by ID."""
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    "DELETE FROM memories WHERE id = ?",
                    (memory_id,),
                )
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def clear_memories(self) -> bool:
        """Delete all long-term memories."""
        try:
            with self._connect() as connection:
                connection.execute("DELETE FROM memories")
            return True
        except sqlite3.Error:
            return False

    def is_safe_to_store(self, text: str) -> bool:
        """Return False when text appears to contain secrets or sensitive data."""
        normalized_text = text.casefold()
        if any(pattern in normalized_text for pattern in self.SENSITIVE_PATTERNS):
            return False
        if is_sensitive_text(text):
            return False

        # Avoid storing long digit sequences that may be cards, IDs, or accounts.
        if re.search(r"\b(?:\d[ -]?){12,19}\b", text):
            return False
        return True

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection configured for row access."""
        connection = sqlite3.connect(self.database_path, timeout=3)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_memory(self, row: sqlite3.Row) -> MemoryRecord:
        """Convert a SQLite row to a MemoryRecord."""
        return MemoryRecord(
            memory_id=int(row["id"]),
            category=str(row["category"]),
            key=str(row["key"]),
            value=str(row["value"]),
            created_at=str(row["created_at"]),
        )

    def _default_database_path(self) -> Path:
        """Return the default memory database path."""
        return MEMORY_DB_PATH
