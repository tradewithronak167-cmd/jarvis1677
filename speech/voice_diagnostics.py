"""Voice system diagnostics for HI ROLEX."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util

from config.settings_manager import SettingsManager
from speech.audio_utils import get_language_code
from speech.microphone_manager import MicrophoneManager
from speech.speaker_manager import SpeakerManager


@dataclass(frozen=True)
class DependencyStatus:
    """Represents whether one voice dependency is installed."""

    name: str
    module: str
    installed: bool


class VoiceDiagnostics:
    """Collects voice package, device, and settings diagnostics."""

    DEPENDENCIES: tuple[tuple[str, str], ...] = (
        ("SpeechRecognition", "speech_recognition"),
        ("PyAudio", "pyaudio"),
        ("pyttsx3", "pyttsx3"),
        ("sounddevice", "sounddevice"),
    )

    def __init__(
        self,
        settings_manager: SettingsManager,
        microphone_manager: MicrophoneManager,
        speaker_manager: SpeakerManager,
    ) -> None:
        self.settings_manager = settings_manager
        self.microphone_manager = microphone_manager
        self.speaker_manager = speaker_manager

    def dependency_statuses(self) -> list[DependencyStatus]:
        """Return install status for required voice packages."""
        statuses: list[DependencyStatus] = []
        for name, module in self.DEPENDENCIES:
            statuses.append(
                DependencyStatus(
                    name=name,
                    module=module,
                    installed=importlib.util.find_spec(module) is not None,
                )
            )
        return statuses

    def devices_report(self) -> str:
        """Return a human-readable microphone and speaker report."""
        microphones = self.microphone_manager.list_microphones()
        speakers = self.speaker_manager.list_speakers()
        return (
            "Microphones:\n"
            f"{self._format_list(microphones)}\n\n"
            "Speakers:\n"
            f"{self._format_list(speakers)}"
        )

    def settings_report(self) -> str:
        """Return a human-readable voice settings report."""
        settings = self.settings_manager.load_settings()
        language = settings.get("language", "English")
        return (
            f"Language: {language} ({get_language_code(language)})\n"
            f"Voice: {settings.get('voice', 'Female')}\n"
            f"Microphone: {settings.get('microphone', 'Default')}\n"
            f"Speaker: {settings.get('speaker', 'Default')}"
        )

    def full_report(self) -> str:
        """Return a complete voice readiness report."""
        dependencies = "\n".join(
            f"{'[OK]' if status.installed else '[MISSING]'} {status.name}"
            for status in self.dependency_statuses()
        )
        return (
            "Voice System Diagnostics\n"
            "========================\n\n"
            "Dependencies:\n"
            f"{dependencies}\n\n"
            "Settings:\n"
            f"{self.settings_report()}\n\n"
            "Devices:\n"
            f"{self.devices_report()}"
        )

    def is_ready(self) -> bool:
        """Return True when all core voice packages are installed."""
        return all(status.installed for status in self.dependency_statuses())

    def _format_list(self, values: list[str]) -> str:
        """Format a list for display in the diagnostics window."""
        return "\n".join(f"- {value}" for value in values) if values else "- Default"
