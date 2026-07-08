"""High-level speech manager for HI ROLEX."""

from __future__ import annotations

from config.settings_manager import SettingsManager
from speech.microphone_manager import MicrophoneManager
from speech.speaker_manager import SpeakerManager
from speech.speech_to_text import SpeechToText
from speech.text_to_speech import TextToSpeech
from speech.voice_diagnostics import VoiceDiagnostics


class SpeechManager:
    """Coordinates speech-to-text, text-to-speech, and audio devices."""

    def __init__(self, settings_manager: SettingsManager) -> None:
        self.settings_manager = settings_manager
        self.microphone_manager = MicrophoneManager()
        self.speaker_manager = SpeakerManager()
        self.speech_to_text = SpeechToText(settings_manager)
        self.text_to_speech = TextToSpeech(settings_manager)
        self.voice_diagnostics = VoiceDiagnostics(
            settings_manager,
            self.microphone_manager,
            self.speaker_manager,
        )

    def listen_once(self) -> str:
        """Listen one time through the speech-to-text module."""
        return self.speech_to_text.listen_once()

    def speak(self, text: str) -> str:
        """Speak text through the text-to-speech module."""
        return self.text_to_speech.speak(text)

    def diagnostics_report(self) -> str:
        """Return a complete voice diagnostics report."""
        return self.voice_diagnostics.full_report()

    def voice_is_ready(self) -> bool:
        """Return True when required voice packages are installed."""
        return self.voice_diagnostics.is_ready()

    def stop(self) -> None:
        """Stop speech input and output activity."""
        self.speech_to_text.stop_listening()
        self.text_to_speech.stop()
