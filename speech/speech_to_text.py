"""Speech-to-text support for HI ROLEX."""

from __future__ import annotations

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
            return "SpeechRecognition or PyAudio is not installed."

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
            return recognizer.recognize_google(audio, language=language_code)
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

    def stop_listening(self) -> None:
        """Stop the current listening state."""
        self.is_listening = False

    def _find_microphone_index(self, microphone_name: str) -> int | None:
        """Resolve a saved microphone name to a SpeechRecognition device index."""
        if microphone_name == "Default":
            return None

        try:
            import speech_recognition as sr

            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if name == microphone_name:
                    return index
        except Exception:
            return None

        return None
