"""Speech-to-text support for HI ROLEX."""

from __future__ import annotations

import audioop
from collections.abc import Callable
import time

from config.settings_manager import SettingsManager
from speech.audio_utils import get_language_code
from utils.logger import get_logger


class SpeechToText:
    """Converts microphone audio into text."""

    def __init__(self, settings_manager: SettingsManager) -> None:
        self.settings_manager = settings_manager
        self.is_listening = False
        self.logger = get_logger()

    def listen(self) -> str:
        """Start one reusable listening operation.

        Continuous listening will be added later. Day 5 intentionally keeps
        this as a safe wrapper around listen_once.
        """
        self.is_listening = True
        return self.listen_once()

    def listen_once(self) -> str:
        """Listen one time and return recognized text or a friendly error."""
        try:
            import speech_recognition as sr
        except Exception:
            return "Speech recognition packages are not installed."

        settings = self.settings_manager.load_settings()
        language_code = get_language_code(settings.get("language", "English"))

        recognizer = sr.Recognizer()
        microphone_index = self._find_microphone_index(
            settings.get("microphone", "Default")
        )

        try:
            with sr.Microphone(device_index=microphone_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            recognized_text = recognizer.recognize_google(audio, language=language_code)
            return recognized_text.strip() or "Could not understand the audio."
        except sr.WaitTimeoutError:
            return "No speech detected."
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError:
            return "Speech recognition service is unavailable."
        except Exception as error:
            self.logger.error("Microphone error: %s", error)
            return f"Microphone error: {error}"
        finally:
            self.is_listening = False

    def microphone_ready(self) -> tuple[bool, str]:
        """Return whether the microphone stack can be opened."""
        try:
            import speech_recognition as sr

            selected_microphone = self.settings_manager.load_settings().get(
                "microphone",
                "Default",
            )
            microphone_index = self._find_microphone_index(selected_microphone)
            with sr.Microphone(device_index=microphone_index):
                device_text = "default input" if microphone_index is None else f"device #{microphone_index}"
                return True, f"Microphone is available using {device_text}."
        except Exception as error:
            self.logger.error("Microphone readiness check failed: %s", error)
            return False, f"Microphone is not available: {error}"

    def measure_microphone_level(
        self,
        duration_seconds: float = 4.0,
        level_callback: Callable[[int], None] | None = None,
    ) -> tuple[bool, str, int]:
        """Measure microphone input level and return the strongest observed beat."""
        try:
            import speech_recognition as sr
        except Exception:
            return False, "Speech recognition packages are not installed.", 0

        selected_microphone = self.settings_manager.load_settings().get(
            "microphone",
            "Default",
        )
        microphone_index = self._find_microphone_index(selected_microphone)
        max_level = 0

        try:
            with sr.Microphone(device_index=microphone_index) as source:
                end_time = time.monotonic() + max(1.0, duration_seconds)
                while time.monotonic() < end_time:
                    chunk = self._read_microphone_chunk(source)
                    rms = audioop.rms(chunk, source.SAMPLE_WIDTH)
                    level = max(0, min(100, int(rms / 75)))
                    max_level = max(max_level, level)
                    if level_callback is not None:
                        level_callback(level)

            if max_level <= 2:
                return (
                    False,
                    "Microphone is connected, but I did not detect a clear voice beat.",
                    max_level,
                )
            return True, f"Microphone beat detected. Peak level: {max_level}%.", max_level
        except Exception as error:
            self.logger.error("Microphone beat test failed: %s", error)
            return False, f"Microphone beat test failed: {error}", max_level

    def stop_listening(self) -> None:
        """Stop the current listening state."""
        self.is_listening = False

    def _find_microphone_index(self, microphone_name: str) -> int | None:
        """Resolve a saved microphone name to a SpeechRecognition device index."""
        if not microphone_name or microphone_name == "Default":
            return None

        try:
            import speech_recognition as sr

            microphones = sr.Microphone.list_microphone_names()
            normalized_target = self._normalize_device_name(microphone_name)

            for index, name in enumerate(microphones):
                if self._normalize_device_name(name) == normalized_target:
                    return index
            for index, name in enumerate(microphones):
                normalized_name = self._normalize_device_name(name)
                if normalized_target in normalized_name or normalized_name in normalized_target:
                    return index
        except Exception:
            return None

        return None

    def _normalize_device_name(self, value: str) -> str:
        """Normalize device names so saved settings survive small driver-name changes."""
        return " ".join(value.casefold().replace("-", " ").replace("_", " ").split())

    def _read_microphone_chunk(self, source: object) -> bytes:
        """Read one microphone chunk while tolerating PyAudio backend differences."""
        try:
            return source.stream.read(source.CHUNK, exception_on_overflow=False)
        except TypeError:
            return source.stream.read(source.CHUNK)
