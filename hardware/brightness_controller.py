"""Windows brightness control for HI ROLEX."""

from __future__ import annotations

from utils.logger import get_logger


class BrightnessController:
    """Gets and sets screen brightness when the display supports it."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def get_brightness(self) -> int | None:
        """Return brightness percent, or None when unavailable."""
        try:
            import screen_brightness_control as sbc

            brightness_values = sbc.get_brightness()
            if not brightness_values:
                return None
            return int(brightness_values[0])
        except Exception as error:
            self.logger.error("Brightness read unavailable: %s", error)
            return None

    def set_brightness(self, percent: int) -> tuple[bool, str]:
        """Set screen brightness to the requested percentage."""
        safe_percent = max(0, min(100, percent))
        try:
            import screen_brightness_control as sbc

            sbc.set_brightness(safe_percent)
            return True, f"Brightness set to {safe_percent}%"
        except Exception as error:
            self.logger.error("Brightness control unavailable: %s", error)
            return False, f"Brightness control unavailable: {error}"

    def is_supported(self) -> bool:
        """Return True when brightness can be read from this device."""
        return self.get_brightness() is not None
