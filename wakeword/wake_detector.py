"""Wake phrase detection for HI ROLEX."""

from __future__ import annotations


class WakeDetector:
    """Detects whether recognized text contains the configured wake phrase."""

    def __init__(self, wake_word: str = "Hi Rolex") -> None:
        self.wake_word = wake_word

    def detect(self, text: str) -> bool:
        """Return True when the wake word appears anywhere in the text."""
        normalized_text = self._normalize(text)
        normalized_wake_word = self._normalize(self.wake_word)
        return normalized_wake_word in normalized_text

    def set_wake_word(self, wake_word: str) -> None:
        """Update the phrase used for wake detection."""
        self.wake_word = wake_word.strip() or "Hi Rolex"

    def _normalize(self, text: str) -> str:
        """Normalize text for case-insensitive wake phrase matching."""
        return " ".join(text.casefold().split())
