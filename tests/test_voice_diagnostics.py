"""Tests for voice diagnostics helpers."""

from __future__ import annotations

from config.settings_manager import SettingsManager
from speech.audio_utils import safe_device_list
from speech.microphone_manager import MicrophoneManager
from speech.speaker_manager import SpeakerManager
from speech.speech_to_text import SpeechToText
from speech.voice_diagnostics import VoiceDiagnostics


def test_voice_diagnostics_report_contains_sections(tmp_path) -> None:
    """Diagnostics report includes packages, settings, and devices."""
    settings_path = tmp_path / "settings.json"
    settings_manager = SettingsManager(settings_path)
    settings_manager.create_default_settings()

    diagnostics = VoiceDiagnostics(
        settings_manager,
        MicrophoneManager(),
        SpeakerManager(),
    )

    report = diagnostics.full_report()

    assert "Dependencies:" in report
    assert "Settings:" in report
    assert "Devices:" in report


def test_voice_diagnostics_dependency_statuses_have_names(tmp_path) -> None:
    """Each dependency status exposes a package name and module."""
    settings_manager = SettingsManager(tmp_path / "settings.json")
    diagnostics = VoiceDiagnostics(
        settings_manager,
        MicrophoneManager(),
        SpeakerManager(),
    )

    statuses = diagnostics.dependency_statuses()

    assert statuses
    assert all(status.name for status in statuses)
    assert all(status.module for status in statuses)


def test_safe_device_list_removes_blanks_and_duplicates() -> None:
    """Device dropdowns should stay clean and readable."""
    devices = safe_device_list(["", " Mic One ", "mic one", "Mic Two"])

    assert devices == ["Mic One", "Mic Two"]


def test_microphone_name_normalization_is_case_and_separator_insensitive(tmp_path) -> None:
    """Saved microphone names should survive small driver-name formatting changes."""
    speech_to_text = SpeechToText(SettingsManager(tmp_path / "settings.json"))

    assert speech_to_text._normalize_device_name("Microphone (Usb Audio Device)") == (
        speech_to_text._normalize_device_name("microphone (USB audio-device)")
    )
