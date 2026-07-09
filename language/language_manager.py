"""Multi-language support for HI ROLEX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.settings_manager import SettingsManager
from utils.app_paths import LANGUAGE_DIR


class LanguageManager:
    """Loads translation files and returns translated UI text."""

    LANGUAGE_FILES: dict[str, str] = {
        "English": "english.json",
        "Tamil": "tamil.json",
        "Hindi": "hindi.json",
        "Telugu": "telugu.json",
        "Malayalam": "malayalam.json",
        "Kannada": "kannada.json",
        "Marathi": "marathi.json",
        "Marwari": "marwari.json",
    }

    def __init__(
        self,
        settings_manager: SettingsManager,
        language_dir: Path | None = None,
    ) -> None:
        self.settings_manager = settings_manager
        self.language_dir = language_dir or LANGUAGE_DIR
        self.current_language = "English"
        self.translations: dict[str, str] = {}
        self.load_language()

    def load_language(self) -> dict[str, str]:
        """Load the language selected in config/settings.json."""
        settings = self.settings_manager.load_settings()
        selected_language = settings.get("language", "English")
        if not self._language_file_exists(selected_language):
            selected_language = "English"

        self.current_language = selected_language
        self.translations = self._load_language_file(selected_language)
        return self.translations

    def translate(self, key: str) -> str:
        """Return translated text for a key, falling back to English or the key."""
        if key in self.translations:
            return self.translations[key]

        english_translations = self._load_language_file("English")
        return english_translations.get(key, key)

    def available_languages(self) -> list[str]:
        """Return languages supported by the application."""
        return list(self.LANGUAGE_FILES.keys())

    def change_language(self, language: str) -> None:
        """Change the active runtime language, falling back to English if needed."""
        if not self._language_file_exists(language):
            language = "English"

        self.current_language = language
        self.translations = self._load_language_file(language)

    def _language_file_exists(self, language: str) -> bool:
        """Check whether a supported language file exists."""
        language_file = self.LANGUAGE_FILES.get(language)
        if language_file is None:
            return False

        return (self.language_dir / language_file).exists()

    def _load_language_file(self, language: str) -> dict[str, str]:
        """Read one translation file with graceful fallback behavior."""
        language_file = self.LANGUAGE_FILES.get(language, self.LANGUAGE_FILES["English"])
        language_path = self.language_dir / language_file

        if not language_path.exists() and language != "English":
            return self._load_language_file("English")

        try:
            with language_path.open("r", encoding="utf-8") as file:
                loaded_translations: Any = json.load(file)
        except (json.JSONDecodeError, OSError):
            if language != "English":
                return self._load_language_file("English")
            return {}

        if not isinstance(loaded_translations, dict):
            return {}

        return {
            str(key): str(value)
            for key, value in loaded_translations.items()
            if isinstance(key, str)
        }
