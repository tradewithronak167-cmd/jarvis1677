"""Hardware safety tests for HI ROLEX."""

from hardware.brightness_controller import BrightnessController
from hardware.hardware_manager import HardwareManager
from hardware.volume_controller import VolumeController


def test_volume_get_does_not_crash() -> None:
    """Volume getter returns a number or None without crashing."""
    volume = VolumeController().get_volume()

    assert volume is None or isinstance(volume, int)


def test_brightness_get_does_not_crash() -> None:
    """Brightness getter returns a number or None without crashing."""
    brightness = BrightnessController().get_brightness()

    assert brightness is None or isinstance(brightness, int)


def test_invalid_hardware_percent_is_rejected() -> None:
    """Invalid volume/brightness values are rejected before hardware calls."""
    manager = HardwareManager()

    assert not manager.set_volume(200)[0]
    assert not manager.set_brightness(-1)[0]
