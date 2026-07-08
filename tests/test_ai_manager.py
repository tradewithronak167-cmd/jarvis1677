"""AI manager tests for HI ROLEX."""

from ai.ai_manager import AIManager
from ai.offline_ai import OfflineAI
from ai.prompt_builder import PromptBuilder
from ai.conversation_manager import ConversationManager
from config.settings_manager import SettingsManager


class OfflineUnavailable:
    """Fake Ollama manager for unavailable offline AI."""

    def check_ollama_running(self) -> bool:
        return False


def test_missing_api_key_returns_friendly_message(tmp_path) -> None:
    """Online mode with missing key returns friendly message."""
    settings_manager = SettingsManager(tmp_path / "settings.json")
    settings = settings_manager.create_default_settings()
    settings["ai_mode"] = "Online"
    settings_manager.save_settings(settings)
    conversation = ConversationManager(tmp_path / "history.json")
    manager = AIManager(conversation, settings_manager)
    manager.online_ai.api_key = ""

    response = manager.ask("hello")

    assert "Online AI is not configured" in response


def test_offline_ai_unavailable_returns_friendly_message(tmp_path) -> None:
    """Offline AI reports unavailable when Ollama is not running."""
    settings_manager = SettingsManager(tmp_path / "settings.json")
    conversation = ConversationManager(tmp_path / "history.json")
    offline_ai = OfflineAI(
        settings_manager,
        PromptBuilder(),
        conversation,
        OfflineUnavailable(),
    )

    assert "Offline AI is not available" in offline_ai.generate_response("hello")
