"""Microphone discovery for HI ROLEX."""

from __future__ import annotations

from speech.audio_utils import safe_device_list


class MicrophoneManager:
    """Detects available microphone input devices."""

    def list_microphones(self) -> list[str]:
        """Return available microphones, falling back to Default on errors."""
        try:
            import speech_recognition as sr

            microphones = sr.Microphone.list_microphone_names()
            return safe_device_list(microphones)
        except Exception:
            return self._list_microphones_with_sounddevice()

    def get_default_microphone(self) -> str:
        """Return the default microphone name."""
        return self.list_microphones()[0]

    def _list_microphones_with_sounddevice(self) -> list[str]:
        """Try sounddevice as a fallback microphone detector."""
        try:
            import sounddevice as sd

            devices = sd.query_devices()
            microphones = [
                str(device["name"])
                for device in devices
                if int(device.get("max_input_channels", 0)) > 0
            ]
            return safe_device_list(microphones)
        except Exception:
            return ["Default"]
