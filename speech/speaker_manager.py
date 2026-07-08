"""Speaker discovery for HI ROLEX."""

from __future__ import annotations

from speech.audio_utils import safe_device_list


class SpeakerManager:
    """Detects available speaker output devices."""

    def list_speakers(self) -> list[str]:
        """Return available speakers, falling back to Default on errors."""
        try:
            import sounddevice as sd

            devices = sd.query_devices()
            speakers = [
                str(device["name"])
                for device in devices
                if int(device.get("max_output_channels", 0)) > 0
            ]
            return safe_device_list(speakers)
        except Exception:
            return ["Default"]

    def get_default_speaker(self) -> str:
        """Return the default speaker name."""
        return self.list_speakers()[0]
