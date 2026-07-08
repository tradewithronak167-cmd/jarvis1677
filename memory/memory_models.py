"""Data models for HI ROLEX memory."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryRecord:
    """Represents one long-term memory row."""

    memory_id: int
    category: str
    key: str
    value: str
    created_at: str


@dataclass(frozen=True)
class ConversationSummary:
    """Represents one stored conversation summary."""

    summary_id: int
    summary: str
    created_at: str
