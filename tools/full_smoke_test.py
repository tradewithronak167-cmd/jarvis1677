"""Full local smoke test for the HI ROLEX desktop assistant."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from assistant.command_router import CommandRouter
from config.settings_manager import SettingsManager
from gui.main_window import MainWindow
from language.language_manager import LanguageManager
from speech.speech_manager import SpeechManager


def main() -> int:
    """Run a broad, non-destructive smoke test."""
    checks: list[tuple[str, bool, str]] = []

    settings_manager = SettingsManager()
    settings = settings_manager.load_settings()
    checks.append(("settings load", bool(settings), "settings.json loaded"))

    language_manager = LanguageManager(settings_manager)
    language_keys_ok = _language_files_have_same_keys(language_manager)
    checks.append(("language files", language_keys_ok, "all language files share keys"))

    router = CommandRouter()
    command_cases = {
        "open notepad": "open_app",
        "close notepad": "close_app",
        "set volume to 50": "hardware_control",
        "what is Python": "ai_chat",
    }
    for command, expected_category in command_cases.items():
        plan = router.create_plan(command)
        actual_category = plan.actions[0].intent.category if plan.actions else ""
        checks.append(
            (
                f"route {command}",
                actual_category == expected_category,
                f"{actual_category} expected {expected_category}",
            )
        )

    speech_manager = SpeechManager(settings_manager)
    checks.append(("voice packages", speech_manager.voice_is_ready(), "voice stack check"))
    checks.append(("jarvis dashboard", _dashboard_widgets_exist(), "command center widgets"))

    failed = False
    print("HI ROLEX Full Smoke Test")
    print("=========================")
    for name, passed, detail in checks:
        status = "OK" if passed else "FAIL"
        print(f"[{status}] {name}: {detail}")
        failed = failed or not passed

    return 1 if failed else 0


def _dashboard_widgets_exist() -> bool:
    """Return True when the command center dashboard can be constructed."""
    try:
        app = MainWindow()
        app.update()
        ready = bool(app.voice_animation and app.activity_textbox and app.metric_labels)
        app.close_application()
        return ready
    except Exception:
        return False


def _language_files_have_same_keys(language_manager: LanguageManager) -> bool:
    """Return True when every language JSON file has the English key set."""
    english_path = language_manager.language_dir / language_manager.LANGUAGE_FILES["English"]
    english_keys = set(_load_json_keys(english_path))
    if not english_keys:
        return False

    for file_name in language_manager.LANGUAGE_FILES.values():
        path = language_manager.language_dir / file_name
        if set(_load_json_keys(path)) != english_keys:
            return False
    return True


def _load_json_keys(path: Path) -> list[str]:
    """Load top-level JSON keys safely."""
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    return [str(key) for key in data]


if __name__ == "__main__":
    raise SystemExit(main())
