"""Internet connectivity checks for HI ROLEX."""

from __future__ import annotations


class InternetChecker:
    """Checks whether the machine appears to have internet access."""

    def is_connected(self) -> bool:
        """Return True when a lightweight HTTP request succeeds quickly."""
        try:
            import requests

            response = requests.get("https://www.google.com/generate_204", timeout=2)
            return response.status_code in {204, 200}
        except Exception:
            return False
