"""Wake-word manager for HI ROLEX."""

from __future__ import annotations

from collections.abc import Callable

from config.settings_manager import SettingsManager
from speech.speech_manager import SpeechManager
from utils.app_paths import ASSETS_DIR
from wakeword.wake_detector import WakeDetector
from wakeword.wake_listener import WakeListener


class WakeWordManager:
    """Coordinates wake detection, wake feedback, and command capture."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        speech_manager: SpeechManager,
        on_status_change: Callable[[str], None],
        on_command_recognized: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        self.settings_manager = settings_manager
        self.speech_manager = speech_manager
        self.on_status_change = on_status_change
        self.on_command_recognized = on_command_recognized
        self.on_error = on_error

        settings = self.settings_manager.load_settings()
        self.wake_detector = WakeDetector(settings.get("wake_word", "Hi Rolex"))
        self.wake_listener = WakeListener(
            settings_manager=self.settings_manager,
            wake_detector=self.wake_detector,
            on_wake_detected=self._handle_wake_detected,
            on_error=self._handle_error,
        )

    def start(self) -> None:
        """Start listening for the wake phrase."""
        self.on_status_change("Sleeping")
        self.wake_listener.start()

    def stop(self) -> None:
        """Stop listening for the wake phrase."""
        self.wake_listener.stop()
        self.speech_manager.stop()
        self.on_status_change("Ready")

    def pause(self) -> None:
        """Pause wake phrase detection."""
        self.wake_listener.pause()
        self.on_status_change("Ready")

    def resume(self) -> None:
        """Resume wake phrase detection."""
        self.wake_listener.resume()
        self.on_status_change("Sleeping")

    def set_wake_word(self, wake_word: str) -> None:
        """Update the wake phrase at runtime."""
        self.wake_detector.set_wake_word(wake_word)

    def _handle_wake_detected(self) -> None:
        """Respond when the wake phrase is detected."""
        self.on_status_change("Listening")
        self._play_wake_sound()
        self.speech_manager.speak("Yes, I'm listening.")
        command = self.speech_manager.listen_once()
        self._handle_command_recognized(command)

    def _handle_command_recognized(self, command: str) -> None:
        """Forward the recognized command to the GUI without executing it."""
        self.on_status_change("Processing")
        self.on_command_recognized(command)
        self.on_status_change("Sleeping")

    def _handle_error(self, message: str) -> None:
        """Forward recoverable wake-listener errors to the GUI."""
        self.on_error(message)
        self.on_status_change("Ready")

    def _play_wake_sound(self) -> None:
        """Play assets/sounds/wake.wav when available."""
        wake_sound_path = ASSETS_DIR / "sounds" / "wake.wav"
        if not wake_sound_path.exists():
            return

        try:
            import winsound

            winsound.PlaySound(
                str(wake_sound_path),
                winsound.SND_FILENAME | winsound.SND_ASYNC,
            )
        except Exception:
            return
