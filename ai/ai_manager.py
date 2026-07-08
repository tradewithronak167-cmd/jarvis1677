"""AI manager for HI ROLEX."""

from __future__ import annotations

from ai.basic_ai import BasicAI
from ai.conversation_manager import ConversationManager
from ai.internet_checker import InternetChecker
from ai.offline_ai import OfflineAI
from ai.online_ai import OnlineAI
from ai.prompt_builder import PromptBuilder
from config.settings_manager import SettingsManager
from memory.conversation_memory import ConversationMemory
from memory.memory_manager import MemoryManager
from memory.profile_manager import ProfileManager


class AIManager:
    """Routes chat messages to the available AI provider."""

    def __init__(
        self,
        conversation_manager: ConversationManager | None = None,
        settings_manager: SettingsManager | None = None,
    ) -> None:
        self.conversation_manager = conversation_manager or ConversationManager()
        self.settings_manager = settings_manager or SettingsManager()
        self.memory_manager = MemoryManager()
        self.profile_manager = ProfileManager()
        self.conversation_memory = ConversationMemory()
        self.prompt_builder = PromptBuilder(
            self.memory_manager,
            self.profile_manager,
            self.conversation_memory,
        )
        self.internet_checker = InternetChecker()
        self.online_ai = OnlineAI(self.prompt_builder, self.conversation_manager)
        self.offline_ai = OfflineAI(
            self.settings_manager,
            self.prompt_builder,
            self.conversation_manager,
        )
        self.basic_ai = BasicAI()
        self.last_provider_used = "Basic AI"

    def ask(self, message: str) -> str:
        """Send a message to the selected AI mode and return the response."""
        cleaned_message = message.strip()
        if not cleaned_message:
            return "Please type a message first."

        memory_response = self._handle_memory_command(cleaned_message)
        if memory_response is not None:
            self.last_provider_used = "Memory"
            self.conversation_manager.add_message("user", cleaned_message)
            self.conversation_manager.add_message("assistant", memory_response)
            return memory_response

        ai_mode = self.get_ai_mode()
        if ai_mode == "Online":
            response = self._ask_online(cleaned_message)
        elif ai_mode == "Offline":
            response = self._ask_offline(cleaned_message)
        else:
            response = self._ask_hybrid(cleaned_message)

        self.conversation_manager.add_message("user", cleaned_message)
        self.conversation_manager.add_message("assistant", response)
        summary = self.conversation_memory.create_summary(
            self.conversation_manager.get_history()
        )
        if summary:
            self.conversation_memory.save_summary(summary)
        return response

    def is_online_available(self) -> bool:
        """Return True when OnlineAI is configured and internet is reachable."""
        return self.online_ai.is_configured() and self.internet_checker.is_connected()

    def is_basic_mode(self) -> bool:
        """Return True when neither OnlineAI nor OfflineAI is available."""
        return not self.is_online_available() and not self.offline_ai.is_available()

    def get_ai_mode(self) -> str:
        """Return the configured AI mode."""
        settings = self.settings_manager.load_settings()
        mode = settings.get("ai_mode", "Hybrid")
        if mode not in {"Online", "Offline", "Hybrid"}:
            return "Hybrid"
        return mode

    def get_status_text(self) -> str:
        """Return a friendly status message for the Chat window."""
        mode = self.get_ai_mode()
        if mode == "Online":
            return "Online AI"
        if mode == "Offline":
            return f"Offline AI ({self.offline_ai.get_model()})"
        return "Hybrid Mode"

    def get_thinking_status(self) -> str:
        """Return the provider status shown while a response is generated."""
        mode = self.get_ai_mode()
        if mode == "Online":
            return "Using Online AI..."
        if mode == "Offline":
            return "Using Offline AI..."
        return "Hybrid Mode is choosing the fastest available AI..."

    def _ask_online(self, message: str) -> str:
        """Use Gemini online AI only."""
        if not self.online_ai.is_configured():
            self.last_provider_used = "AI unavailable"
            return self.online_ai.MISSING_KEY_MESSAGE
        if not self.internet_checker.is_connected():
            self.last_provider_used = "AI unavailable"
            return "Internet connection is unavailable. Online AI cannot respond."

        self.last_provider_used = "Online AI"
        return self.online_ai.generate_response(message)

    def _ask_offline(self, message: str) -> str:
        """Use Ollama offline AI only."""
        if not self.offline_ai.is_available():
            self.last_provider_used = "AI unavailable"
            return self.offline_ai.UNAVAILABLE_MESSAGE

        self.last_provider_used = "Offline AI"
        return self.offline_ai.generate_response(message)

    def _ask_hybrid(self, message: str) -> str:
        """Use OnlineAI when available, otherwise fallback to OfflineAI."""
        if self.is_online_available():
            self.last_provider_used = "Online AI"
            response = self.online_ai.generate_response(message)
            if not response.startswith("Online AI error:"):
                return response

        if self.offline_ai.is_available():
            self.last_provider_used = "Offline AI"
            return self.offline_ai.generate_response(message)

        self.last_provider_used = "AI unavailable"
        return (
            "AI unavailable. Configure Gemini for Online AI, or install Ollama "
            "and run a local model for Offline AI.\n\n"
            f"Basic answer: {self.basic_ai.generate_response(message)}"
        )

    def _handle_memory_command(self, message: str) -> str | None:
        """Handle explicit memory commands typed in chat."""
        lowered = message.casefold().strip()
        if lowered.startswith("remember my name is "):
            name = message[len("remember my name is ") :].strip()
            if not name or not self.memory_manager.is_safe_to_store(name):
                return "I cannot safely save that memory."
            self.profile_manager.set_profile_value("display_name", name)
            self.memory_manager.add_memory("profile", "name", name)
            return f"I will remember your name is {name}."

        if lowered.startswith("remember that "):
            memory_text = message[len("remember that ") :].strip()
            if not memory_text or not self.memory_manager.is_safe_to_store(memory_text):
                return "I cannot safely save that memory."
            key = self._memory_key_from_text(memory_text)
            if self.memory_manager.add_memory("user", key, memory_text):
                return "I saved that memory."
            return "I could not save that memory."

        if lowered == "what do you remember about me":
            return self._format_remembered_information()

        if lowered == "forget my name":
            deleted_any = False
            for memory in self.memory_manager.search_memories("name"):
                deleted_any = self.memory_manager.delete_memory(memory.memory_id) or deleted_any
            self.profile_manager.set_profile_value("display_name", "")
            return "I forgot your saved name." if deleted_any else "I did not have your name saved."

        return None

    def _memory_key_from_text(self, text: str) -> str:
        """Create a simple searchable key from memory text."""
        words = [word.strip(".,!?;:").casefold() for word in text.split()]
        useful_words = [word for word in words if word and word not in {"i", "my", "that"}]
        return "_".join(useful_words[:4]) or "memory"

    def _format_remembered_information(self) -> str:
        """Return a safe summary of saved profile and memories."""
        lines: list[str] = []
        profile = self.profile_manager.get_profile()
        if profile:
            for key, value in profile.items():
                if value and self.memory_manager.is_safe_to_store(value):
                    lines.append(f"{key}: {value}")

        for memory in self.memory_manager.get_all_memories()[:10]:
            text = f"{memory.key}: {memory.value}"
            if self.memory_manager.is_safe_to_store(text):
                lines.append(text)

        if not lines:
            return "I do not have any saved memories about you yet."
        return "Here is what I remember:\n" + "\n".join(lines[:10])
