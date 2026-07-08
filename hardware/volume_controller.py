"""Windows volume control for HI ROLEX."""

from __future__ import annotations

from utils.logger import get_logger


class VolumeController:
    """Gets and sets the Windows master volume when pycaw is available."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def get_volume(self) -> int | None:
        """Return current volume percent, or None when unavailable."""
        try:
            endpoint = self._get_endpoint_volume()
            return round(endpoint.GetMasterVolumeLevelScalar() * 100)
        except Exception as error:
            self.logger.error("Volume read unavailable: %s", error)
            return None

    def set_volume(self, percent: int) -> tuple[bool, str]:
        """Set Windows master volume to the requested percentage."""
        safe_percent = max(0, min(100, percent))
        try:
            endpoint = self._get_endpoint_volume()
            endpoint.SetMasterVolumeLevelScalar(safe_percent / 100, None)
            return True, f"Volume set to {safe_percent}%"
        except Exception as error:
            self.logger.error("Volume control unavailable: %s", error)
            return False, f"Volume control unavailable: {error}"

    def _get_endpoint_volume(self) -> object:
        """Create a pycaw endpoint volume controller."""
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        speakers = AudioUtilities.GetSpeakers()
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return interface.QueryInterface(IAudioEndpointVolume)
