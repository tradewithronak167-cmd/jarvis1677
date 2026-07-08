"""Language tests for HI ROLEX."""

from config.settings_manager import SettingsManager
from language.language_manager import LanguageManager


def test_english_translations_load(tmp_path) -> None:
    """English translations are available."""
    settings_manager = SettingsManager(tmp_path / "settings.json")
    language_manager = LanguageManager(settings_manager)

    assert language_manager.translate("settings") == "Settings"


def test_missing_translation_falls_back_safely(tmp_path) -> None:
    """Missing translation returns key when English also misses it."""
    settings_manager = SettingsManager(tmp_path / "settings.json")
    language_manager = LanguageManager(settings_manager)

    assert language_manager.translate("missing_key_for_test") == "missing_key_for_test"
