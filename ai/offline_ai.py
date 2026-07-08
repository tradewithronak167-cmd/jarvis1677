"""Offline Ollama AI provider for HI ROLEX."""

from __future__ import annotations

from config.settings_manager import SettingsManager
from ai.conversation_manager import ConversationManager
from ai.ollama_manager import OllamaManager
from ai.prompt_builder import PromptBuilder


class OfflineAI:
    """Offline AI provider powered by a local Ollama server."""

    UNAVAILABLE_MESSAGE: str = (
        "Offline AI is not available. Please install Ollama and run a local model."
    )

    def __init__(
        self,
        settings_manager: SettingsManager,
        prompt_builder: PromptBuilder,
        conversation_manager: ConversationManager,
        ollama_manager: OllamaManager | None = None,
    ) -> None:
        self.settings_manager = settings_manager
        self.prompt_builder = prompt_builder
        self.conversation_manager = conversation_manager
        self.ollama_manager = ollama_manager or OllamaManager()

    def is_available(self) -> bool:
        """Return True when Ollama is running locally."""
        return self.ollama_manager.check_ollama_running()

    def generate_response(self, user_message: str) -> str:
        """Generate an offline AI response using Ollama."""
        if not self.is_available():
            return self.UNAVAILABLE_MESSAGE

        prompt = self.prompt_builder.build_prompt(
            user_message,
            self.conversation_manager.get_history(),
        )
        response = self.ollama_manager.generate(self.get_model(), prompt)
        return response or "Offline AI did not return a response."

    def get_model(self) -> str:
        """Return the configured Ollama model name."""
        settings = self.settings_manager.load_settings()
        return settings.get("offline_model", "qwen2.5:3b")

    def set_model(self, model_name: str) -> None:
        """Save a new Ollama model name in settings."""
        settings = self.settings_manager.load_settings()
        settings["offline_model"] = model_name.strip() or "qwen2.5:3b"
        self.settings_manager.save_settings(settings)
