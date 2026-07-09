"""Text-to-speech support for HI ROLEX."""

from __future__ import annotations

import threading

from config.settings_manager import SettingsManager
from utils.logger import get_logger


class TextToSpeech:
    """Speaks text using the local Windows text-to-speech engine."""

    def __init__(self, settings_manager: SettingsManager) -> None:
        self.settings_manager = settings_manager
        self.engine = None
        self.logger = get_logger()
        self._speech_lock = threading.RLock()
        self._initialize_engine()

    def speak(self, text: str) -> str:
        """Speak text aloud and return a status message."""
        if self.engine is None:
            return "Text-to-speech engine is not available."

        with self._speech_lock:
            try:
                self.set_voice()
                self.engine.say(text)
                self.engine.runAndWait()
                return "Speech completed."
            except Exception as error:
                self.logger.error("Speaker error: %s", error)
                return f"Speaker error: {error}"

    def stop(self) -> None:
        """Stop current speech output."""
        if self.engine is None:
            return

        with self._speech_lock:
            try:
                self.engine.stop()
            except Exception:
                return

    def set_voice(self) -> None:
        """Select the saved voice preference when available."""
        if self.engine is None:
            return

        settings = self.settings_manager.load_settings()
        preferred_voice = settings.get("voice", "Female").strip()
        if not preferred_voice or preferred_voice == "Default":
            return

        preferred_voice_lower = preferred_voice.lower()

        try:
            voices = self.engine.getProperty("voices")
            for voice in voices:
                voice_text = f"{voice.name} {voice.id}".lower()
                if preferred_voice_lower == str(voice.name).lower():
                    self.engine.setProperty("voice", voice.id)
                    return
            for voice in voices:
                voice_text = f"{voice.name} {voice.id}".lower()
                if preferred_voice_lower in voice_text:
                    self.engine.setProperty("voice", voice.id)
                    return
        except Exception:
            return

    def set_rate(self, rate: int) -> None:
        """Set speech speed."""
        if self.engine is not None:
            safe_rate = max(80, min(260, rate))
            self.engine.setProperty("rate", safe_rate)

    def set_volume(self, volume: float) -> None:
        """Set speech volume between 0.0 and 1.0."""
        if self.engine is not None:
            safe_volume = max(0.0, min(1.0, volume))
            self.engine.setProperty("volume", safe_volume)

    def list_voices(self) -> list[str]:
        """Return available local TTS voices."""
        if self.engine is None:
            return ["Text-to-speech engine is not available."]

        try:
            voices = self.engine.getProperty("voices")
            return [str(getattr(voice, "name", "Unknown voice")) for voice in voices]
        except Exception as error:
            self.logger.error("Voice listing failed: %s", error)
            return [f"Voice listing failed: {error}"]

    def speaker_ready(self) -> tuple[bool, str]:
        """Return whether the TTS engine is ready."""
        if self.engine is None:
            return False, "Text-to-speech engine is not available."
        return True, "Text-to-speech engine is available."

    def _initialize_engine(self) -> None:
        """Initialize pyttsx3 without crashing the app."""
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
        except Exception as error:
            self.logger.error("Text-to-speech initialization failed: %s", error)
            self.engine = None
