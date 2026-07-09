"""Prompt construction for HI ROLEX online chat."""

from __future__ import annotations

from config.settings_manager import SettingsManager
from memory.conversation_memory import ConversationMemory
from memory.memory_manager import MemoryManager
from memory.profile_manager import ProfileManager


class PromptBuilder:
    """Builds safe, consistent prompts for the online AI provider."""

    SYSTEM_PROMPT: str = (
        "You are HI ROLEX, a helpful Windows desktop AI assistant.\n"
        "Speak like a natural voice assistant talking to Ronak.\n"
        "Use short, clear sentences that sound good when read aloud.\n"
        "Be friendly, practical, and safe.\n"
        "Do not execute dangerous commands without confirmation."
    )

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        profile_manager: ProfileManager | None = None,
        conversation_memory: ConversationMemory | None = None,
        settings_manager: SettingsManager | None = None,
    ) -> None:
        self.memory_manager = memory_manager or MemoryManager()
        self.profile_manager = profile_manager or ProfileManager()
        self.conversation_memory = conversation_memory or ConversationMemory()
        self.settings_manager = settings_manager or SettingsManager()

    def build_prompt(self, user_message: str, history: list[dict[str, str]]) -> str:
        """Create a full prompt from the system prompt, history, and user message."""
        history_text = self._format_history(history)
        memory_text = self._format_memory_context()
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Reply language instruction:\n{self._language_instruction()}\n\n"
            f"Safe local memory context:\n{memory_text}\n\n"
            f"Conversation history:\n{history_text}\n\n"
            f"User: {user_message}\n"
            "HI ROLEX:"
        )

    def _language_instruction(self) -> str:
        """Return a short instruction for the selected response language."""
        language = self.settings_manager.load_settings().get("language", "English")
        if language == "Marwari":
            return (
                "Reply in simple Marwari/Rajasthani style when possible. "
                "If exact Marwari is uncertain, use easy Hindi with Marwari-flavored words."
            )
        return f"Reply in {language} unless the user clearly asks for another language."

    def _format_history(self, history: list[dict[str, str]]) -> str:
        """Format recent conversation messages for the model."""
        if not history:
            return "No previous conversation."

        recent_messages = history[-12:]
        lines = []
        for message in recent_messages:
            role = message.get("role", "unknown").title()
            content = message.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _format_memory_context(self) -> str:
        """Format a small safe memory context for AI providers."""
        lines: list[str] = []
        profile = self.profile_manager.get_profile()
        for key in ("display_name", "preferred_language", "preferred_voice"):
            value = profile.get(key)
            if value and self.memory_manager.is_safe_to_store(value):
                lines.append(f"{key.replace('_', ' ').title()}: {value[:120]}")

        for memory in self.memory_manager.get_all_memories()[:7]:
            text = f"{memory.key}: {memory.value}"
            if self.memory_manager.is_safe_to_store(text):
                lines.append(text[:160])

        for summary in self.conversation_memory.get_recent_summaries(limit=2):
            if self.memory_manager.is_safe_to_store(summary.summary):
                lines.append(f"Recent summary: {summary.summary[:180]}")

        if not lines:
            return "No safe saved memories."
        return "\n".join(lines[:10])
