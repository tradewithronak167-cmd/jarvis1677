"""Internet connectivity checks for HI ROLEX."""

from __future__ import annotations

import time


class InternetChecker:
    """Checks whether the machine appears to have internet access."""

    CACHE_SECONDS: float = 20.0

    def __init__(self) -> None:
        self._last_checked_at = 0.0
        self._last_result = False

    def is_connected(self) -> bool:
        """Return True when a lightweight HTTP request succeeds quickly."""
        now = time.monotonic()
        if now - self._last_checked_at < self.CACHE_SECONDS:
            return self._last_result

        try:
            import requests

            response = requests.get("https://www.google.com/generate_204", timeout=0.8)
            self._last_result = response.status_code in {204, 200}
        except Exception:
            self._last_result = False

        self._last_checked_at = now
        return self._last_result
