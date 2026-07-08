"""Built-in basic chat fallback for HI ROLEX."""

from __future__ import annotations


class BasicAI:
    """Small rule-based assistant that works without API keys or packages."""

    def generate_response(self, user_message: str) -> str:
        """Return a helpful response for common HI ROLEX questions."""
        message = " ".join(user_message.casefold().split())

        if self._contains_any(message, ["hello", "hi", "hey"]):
            return "Hello. I am HI ROLEX. Basic AI mode is working."

        if self._contains_any(message, ["what can you do", "help", "features"]):
            return (
                "I can help you with chat, settings, language, voice testing, "
                "wake word setup, app launching, file management, and hardware status. "
                "Some advanced AI features need an API key later."
            )

        if self._contains_any(message, ["open chrome", "open notepad", "open calculator"]):
            return (
                "You can use the automation system for that. Try saying or typing "
                "commands like: open chrome, open notepad, or open calculator."
            )

        if self._contains_any(message, ["file", "folder", "delete", "rename", "copy", "move"]):
            return (
                "Use the Files button to open the File Manager. It can create, rename, "
                "copy, move, open, search, and delete local files with confirmation."
            )

        if self._contains_any(message, ["hardware", "cpu", "ram", "battery", "volume"]):
            return (
                "Use the Hardware button to view CPU, RAM, disk, battery, network, "
                "volume, brightness, and system information."
            )

        if self._contains_any(message, ["voice", "microphone", "speaker"]):
            return (
                "Use the Microphone button to open the Voice Test window. "
                "Full microphone features need PyAudio installed."
            )

        if self._contains_any(message, ["api key", "gemini", "online ai"]):
            return (
                "Online AI needs GEMINI_API_KEY in a .env file. Until then, "
                "I will continue answering in Basic AI mode."
            )

        return (
            "I am running in Basic AI mode, so I can answer simple HI ROLEX questions. "
            "For smarter answers, add a Gemini API key later."
        )

    def _contains_any(self, message: str, keywords: list[str]) -> bool:
        """Return True when any keyword appears in the message."""
        return any(keyword in message for keyword in keywords)
