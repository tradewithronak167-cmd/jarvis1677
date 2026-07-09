"""Text-to-speech support for HI ROLEX."""

from __future__ import annotations

import threading

from config.settings_manager import SettingsManager
from utils.logger import get_logger


class TextToSpeech:
    """Speaks text using the local Windows text-to-speech engine."""

    VOICE_STYLE_SETTINGS: dict[str, tuple[str | None, int, float]] = {
        "male": ("male", 170, 0.95),
        "male - deep": ("male", 135, 1.0),
        "male - smooth": ("male", 160, 0.95),
        "male - light": ("male", 190, 0.9),
        "male - slight": ("male", 185, 0.88),
        "male - dim": ("male", 140, 0.75),
        "female": ("female", 175, 0.95),
        "female - deep": ("female", 145, 1.0),
        "female - smooth": ("female", 165, 0.95),
        "female - light": ("female", 195, 0.9),
        "female - slight": ("female", 190, 0.88),
        "female - dim": ("female", 150, 0.75),
    }

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
        style = self.VOICE_STYLE_SETTINGS.get(preferred_voice_lower)

        try:
            voices = self.engine.getProperty("voices")
            if style is not None:
                gender, rate, volume = style
                self.set_rate(rate)
                self.set_volume(volume)
                self._select_gender_voice(voices, gender)
                return

            for voice in voices:
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

    def _select_gender_voice(self, voices: object, gender: str | None) -> None:
        """Pick the closest installed Windows voice for a friendly gender/style option."""
        if gender is None:
            return

        for voice in voices:
            voice_text = f"{getattr(voice, 'name', '')} {getattr(voice, 'id', '')}".lower()
            if gender in voice_text:
                self.engine.setProperty("voice", voice.id)
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
