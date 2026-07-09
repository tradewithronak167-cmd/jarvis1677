"""Shared audio helpers for HI ROLEX."""

from __future__ import annotations


LANGUAGE_CODES: dict[str, str] = {
    "English": "en-US",
    "Tamil": "ta-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Malayalam": "ml-IN",
    "Kannada": "kn-IN",
    "Marathi": "mr-IN",
    "Marwari": "hi-IN",
}


def get_language_code(language_name: str) -> str:
    """Return the speech-recognition language code for a saved language name."""
    return LANGUAGE_CODES.get(language_name, LANGUAGE_CODES["English"])


def safe_device_list(devices: list[str]) -> list[str]:
    """Return a non-empty device list for GUI dropdowns."""
    cleaned_devices: list[str] = []
    seen: set[str] = set()
    for device in devices:
        cleaned_device = device.strip()
        if not cleaned_device:
            continue
        normalized_device = " ".join(cleaned_device.casefold().split())
        if normalized_device in seen:
            continue
        seen.add(normalized_device)
        cleaned_devices.append(cleaned_device)
    return cleaned_devices or ["Default"]
