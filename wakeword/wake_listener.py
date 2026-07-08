"""Background wake-word listener for HI ROLEX."""

from __future__ import annotations

from collections.abc import Callable
import threading
import time

from config.settings_manager import SettingsManager
from speech.audio_utils import get_language_code
from wakeword.wake_detector import WakeDetector


class WakeListener:
    """Continuously listens for the wake phrase in a background thread."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        wake_detector: WakeDetector,
        on_wake_detected: Callable[[], None],
        on_error: Callable[[str], None],
    ) -> None:
        self.settings_manager = settings_manager
        self.wake_detector = wake_detector
        self.on_wake_detected = on_wake_detected
        self.on_error = on_error
        self._is_running = False
        self._is_paused = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the background listening thread."""
        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background listening thread."""
        self._is_running = False
        self._is_paused = False

    def pause(self) -> None:
        """Temporarily pause wake detection."""
        self._is_paused = True

    def resume(self) -> None:
        """Resume wake detection after a pause."""
        self._is_paused = False

    def _listen_loop(self) -> None:
        """Run wake detection until stopped."""
        try:
            import speech_recognition as sr
        except Exception:
            self.on_error("SpeechRecognition or PyAudio is not installed.")
            self._is_running = False
            return

        recognizer = sr.Recognizer()

        while self._is_running:
            if self._is_paused:
                time.sleep(0.2)
                continue

            settings = self.settings_manager.load_settings()
            language_code = get_language_code(settings.get("language", "English"))
            microphone_index = self._find_microphone_index(
                settings.get("microphone", "Default"), sr
            )

            try:
                with sr.Microphone(device_index=microphone_index) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=4)
                text = recognizer.recognize_google(audio, language=language_code)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                self.on_error("Speech recognition service is unavailable.")
                time.sleep(2)
                continue
            except Exception as error:
                self.on_error(f"Microphone error: {error}")
                if "pyaudio" in str(error).casefold():
                    self._is_running = False
                    return
                time.sleep(2)
                continue

            if self.wake_detector.detect(text):
                self.on_wake_detected()

    def _find_microphone_index(
        self,
        microphone_name: str,
        speech_recognition_module: object,
    ) -> int | None:
        """Resolve a saved microphone name to a SpeechRecognition device index."""
        if microphone_name == "Default":
            return None

        try:
            for index, name in enumerate(
                speech_recognition_module.Microphone.list_microphone_names()
            ):
                if name == microphone_name:
                    return index
        except Exception:
            return None

        return None
