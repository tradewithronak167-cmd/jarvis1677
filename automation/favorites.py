"""Favorite file and folder storage for HI ROLEX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FavoritesManager:
    """Persists favorite local paths to data/favorites.json."""

    def __init__(self, favorites_path: Path | None = None) -> None:
        self.favorites_path = favorites_path or self._default_path("favorites.json")

    def add_favorite(self, path: str) -> tuple[bool, str]:
        """Add a path to favorites."""
        favorites = self.get_favorites()
        normalized_path = str(Path(path.strip()).expanduser())
        if normalized_path in favorites:
            return False, f"Favorite already exists: {normalized_path}"
        favorites.append(normalized_path)
        self._save_favorites(favorites)
        return True, f"Added favorite: {normalized_path}"

    def remove_favorite(self, path: str) -> tuple[bool, str]:
        """Remove a path from favorites."""
        favorites = self.get_favorites()
        normalized_path = str(Path(path.strip()).expanduser())
        if normalized_path not in favorites:
            return False, f"Favorite not found: {normalized_path}"
        favorites.remove(normalized_path)
        self._save_favorites(favorites)
        return True, f"Removed favorite: {normalized_path}"

    def get_favorites(self) -> list[str]:
        """Return saved favorite paths."""
        if not self.favorites_path.exists():
            self._save_favorites([])
            return []

        try:
            data: Any = json.loads(self.favorites_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._save_favorites([])
            return []

        if not isinstance(data, list):
            self._save_favorites([])
            return []
        return [str(item) for item in data if isinstance(item, str)]

    def _save_favorites(self, favorites: list[str]) -> None:
        """Write favorites to disk."""
        self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
        self.favorites_path.write_text(
            json.dumps(favorites, indent=4),
            encoding="utf-8",
        )

    def _default_path(self, filename: str) -> Path:
        """Return a project data path."""
        return Path(__file__).resolve().parents[1] / "data" / filename
