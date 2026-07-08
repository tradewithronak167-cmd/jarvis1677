"""Tests for voice diagnostics helpers."""

from __future__ import annotations

from config.settings_manager import SettingsManager
from speech.microphone_manager import MicrophoneManager
from speech.speaker_manager import SpeakerManager
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
