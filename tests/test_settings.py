"""Settings tests for HI ROLEX."""

from config.settings_manager import SettingsManager


def test_default_settings_can_load(tmp_path) -> None:
    """Missing settings file creates defaults."""
    manager = SettingsManager(tmp_path / "settings.json")

    settings = manager.load_settings()

    assert settings["language"] == "English"
    assert settings["ai_mode"] == "Hybrid"


def test_settings_can_save(tmp_path) -> None:
    """Settings can be saved and loaded."""
    manager = SettingsManager(tmp_path / "settings.json")
    settings = manager.create_default_settings()
    settings["theme"] = "Light"

    manager.save_settings(settings)

    assert manager.load_settings()["theme"] == "Light"


def test_invalid_settings_json_does_not_crash(tmp_path) -> None:
    """Invalid JSON recovers to defaults."""
    path = tmp_path / "settings.json"
    path.write_text("{not valid json", encoding="utf-8")
    manager = SettingsManager(path)

    settings = manager.load_settings()

    assert settings["wake_word"] == "Hi Rolex"
