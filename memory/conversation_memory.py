"""Conversation summary memory for HI ROLEX."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from memory.memory_manager import MemoryManager
from memory.memory_models import ConversationSummary


class ConversationMemory:
    """Stores short useful conversation summaries."""

    def __init__(self, database_path: Path | None = None) -> None:
        self.memory_manager = MemoryManager(database_path)

    def create_summary(self, messages: list[dict[str, str]]) -> str:
        """Create a short safe summary from recent messages."""
        if not messages:
            return ""

        useful_parts: list[str] = []
        for message in messages[-6:]:
            role = message.get("role", "unknown")
            content = " ".join(message.get("content", "").split())
            if content and self.memory_manager.is_safe_to_store(content):
                useful_parts.append(f"{role}: {content[:160]}")

        return " | ".join(useful_parts)[:500]

    def save_summary(self, summary: str) -> bool:
        """Save a safe short conversation summary."""
        if not summary.strip() or not self.memory_manager.is_safe_to_store(summary):
            return False

        try:
            with self.memory_manager._connect() as connection:
                connection.execute(
                    "INSERT INTO conversation_summaries (summary) VALUES (?)",
                    (summary.strip(),),
                )
            return True
        except sqlite3.Error:
            return False

    def get_recent_summaries(self, limit: int = 5) -> list[ConversationSummary]:
        """Return recent conversation summaries."""
        safe_limit = max(1, min(20, limit))
        try:
            with self.memory_manager._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT id, summary, created_at
                    FROM conversation_summaries
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (safe_limit,),
                ).fetchall()
            return [
                ConversationSummary(
                    summary_id=int(row["id"]),
                    summary=str(row["summary"]),
                    created_at=str(row["created_at"]),
                )
                for row in rows
            ]
        except sqlite3.Error:
            return []
