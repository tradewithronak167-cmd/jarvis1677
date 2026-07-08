"""Browser actions for HI ROLEX automation."""

from __future__ import annotations

from urllib.parse import quote_plus
import webbrowser


class BrowserManager:
    """Opens websites and Google searches in the default browser."""

    def open_website(self, url: str) -> tuple[bool, str]:
        """Open a website URL in the default browser."""
        normalized_url = self._normalize_url(url)
        try:
            webbrowser.open(normalized_url)
            return True, f"Opened website: {normalized_url}"
        except Exception as error:
            return False, f"Could not open website: {error}"

    def google_search(self, query: str) -> tuple[bool, str]:
        """Open a Google search for the given query."""
        if not query.strip():
            return False, "Google search query is empty."

        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        return self.open_website(search_url)

    def _normalize_url(self, url: str) -> str:
        """Ensure a URL includes a browser-friendly scheme."""
        cleaned_url = url.strip()
        if cleaned_url.startswith(("http://", "https://")):
            return cleaned_url
        return f"https://{cleaned_url}"
