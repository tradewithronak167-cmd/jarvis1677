"""Local file search utilities for HI ROLEX."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path


class FileSearch:
    """Searches local folders by name, extension, and recent modification time."""

    def search_by_name(self, folder: str, pattern: str) -> list[str]:
        """Search recursively for files or folders whose names contain pattern."""
        folder_path = self._resolve_folder(folder)
        if not folder_path.is_dir():
            return []

        normalized_pattern = pattern.casefold().strip()
        return [
            str(path)
            for path in folder_path.rglob("*")
            if normalized_pattern in path.name.casefold()
        ]

    def search_by_extension(self, folder: str, extension: str) -> list[str]:
        """Search recursively for files with the given extension."""
        folder_path = self._resolve_folder(folder)
        if not folder_path.is_dir():
            return []

        normalized_extension = extension.strip()
        if not normalized_extension.startswith("."):
            normalized_extension = f".{normalized_extension}"

        return [
            str(path)
            for path in folder_path.rglob(f"*{normalized_extension}")
            if path.is_file()
        ]

    def search_recent(self, folder: str) -> list[str]:
        """Return files modified in the last seven days."""
        folder_path = self._resolve_folder(folder)
        if not folder_path.is_dir():
            return []

        recent_cutoff = datetime.now() - timedelta(days=7)
        results: list[str] = []
        for path in folder_path.rglob("*"):
            try:
                modified_time = datetime.fromtimestamp(path.stat().st_mtime)
            except OSError:
                continue
            if path.is_file() and modified_time >= recent_cutoff:
                results.append(str(path))
        return results

    def _resolve_folder(self, folder: str) -> Path:
        """Resolve relative search folders under the user's Documents folder."""
        folder_path = Path(folder.strip()).expanduser()
        if folder_path.is_absolute():
            return folder_path
        return Path.home() / "Documents" / folder_path
