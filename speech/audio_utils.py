"""Shared audio helpers for HI ROLEX."""

from __future__ import annotations


LANGUAGE_CODES: dict[str, str] = {
    "English": "en-US",
    "Tamil": "ta-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Malayalam": "ml-IN",
    "Kannada": "kn-IN",
}


def get_language_code(language_name: str) -> str:
    """Return the speech-recognition language code for a saved language name."""
    return LANGUAGE_CODES.get(language_name, LANGUAGE_CODES["English"])


def safe_device_list(devices: list[str]) -> list[str]:
    """Return a non-empty device list for GUI dropdowns."""
    cleaned_devices = [device for device in devices if device.strip()]
    return cleaned_devices or ["Default"]
