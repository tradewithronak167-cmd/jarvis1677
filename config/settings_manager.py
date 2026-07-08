"""Settings persistence for HI ROLEX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.app_paths import SETTINGS_PATH
from utils.logger import get_logger


class SettingsManager:
    """Loads, saves, and creates application settings."""

    DEFAULT_SETTINGS: dict[str, str] = {
        "language": "English",
        "theme": "Dark",
        "ai_mode": "Hybrid",
        "offline_model": "qwen2.5:3b",
        "wake_word": "Hi Rolex",
        "voice": "Female",
        "microphone": "Default",
        "speaker": "Default",
    }

    def __init__(self, settings_path: Path | None = None) -> None:
        self.settings_path = settings_path or SETTINGS_PATH
        self.logger = get_logger()

    def create_default_settings(self) -> dict[str, str]:
        """Create settings.json with safe default values."""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.save_settings(self.DEFAULT_SETTINGS)
        return self.DEFAULT_SETTINGS.copy()

    def load_settings(self) -> dict[str, str]:
        """Load settings from disk, recovering gracefully from missing or invalid JSON."""
        if not self.settings_path.exists():
            return self.create_default_settings()

        try:
            with self.settings_path.open("r", encoding="utf-8") as settings_file:
                loaded_settings: Any = json.load(settings_file)
        except (json.JSONDecodeError, OSError) as error:
            self.logger.error("Settings load failed, recreating defaults: %s", error)
            return self.create_default_settings()

        if not isinstance(loaded_settings, dict):
            return self.create_default_settings()

        # Keep new defaults available even if an older settings file misses keys.
        settings = self.DEFAULT_SETTINGS.copy()
        for key, value in loaded_settings.items():
            if key in settings and isinstance(value, str):
                settings[key] = value

        return settings

    def save_settings(self, settings: dict[str, str]) -> None:
        """Save settings to config/settings.json."""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.settings_path.open("w", encoding="utf-8") as settings_file:
                json.dump(settings, settings_file, indent=4)
        except OSError as error:
            self.logger.error("Settings save failed: %s", error)
