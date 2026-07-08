"""Text-to-speech support for HI ROLEX."""

from __future__ import annotations

from config.settings_manager import SettingsManager


class TextToSpeech:
    """Speaks text using the local Windows text-to-speech engine."""

    def __init__(self, settings_manager: SettingsManager) -> None:
        self.settings_manager = settings_manager
        self.engine = None
        self._initialize_engine()

    def speak(self, text: str) -> str:
        """Speak text aloud and return a status message."""
        if self.engine is None:
            return "Text-to-speech engine is not available."

        try:
            self.set_voice()
            self.engine.say(text)
            self.engine.runAndWait()
            return "Speaker test completed."
        except Exception as error:
            return f"Speaker error: {error}"

    def stop(self) -> None:
        """Stop current speech output."""
        if self.engine is None:
            return

        try:
            self.engine.stop()
        except Exception:
            return

    def set_voice(self) -> None:
        """Select the saved Male or Female voice when available."""
        if self.engine is None:
            return

        settings = self.settings_manager.load_settings()
        preferred_voice = settings.get("voice", "Female").lower()

        try:
            voices = self.engine.getProperty("voices")
            for voice in voices:
                voice_text = f"{voice.name} {voice.id}".lower()
                if preferred_voice in voice_text:
                    self.engine.setProperty("voice", voice.id)
                    return
        except Exception:
            return

    def set_rate(self, rate: int) -> None:
        """Set speech speed."""
        if self.engine is not None:
            self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float) -> None:
        """Set speech volume between 0.0 and 1.0."""
        if self.engine is not None:
            safe_volume = max(0.0, min(1.0, volume))
            self.engine.setProperty("volume", safe_volume)

    def _initialize_engine(self) -> None:
        """Initialize pyttsx3 without crashing the app."""
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
        except Exception:
            self.engine = None
