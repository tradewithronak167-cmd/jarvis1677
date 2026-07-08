"""Hardware management facade for HI ROLEX."""

from __future__ import annotations

from hardware.battery_monitor import BatteryMonitor
from hardware.brightness_controller import BrightnessController
from hardware.cpu_monitor import CPUMonitor
from hardware.disk_monitor import DiskMonitor
from hardware.network_monitor import NetworkMonitor
from hardware.ram_monitor import RAMMonitor
from hardware.system_info import SystemInfo
from hardware.volume_controller import VolumeController
from utils.validators import is_valid_percent


class HardwareManager:
    """Coordinates Windows hardware monitoring and basic controls."""

    def __init__(self) -> None:
        self.system_info = SystemInfo()
        self.cpu_monitor = CPUMonitor()
        self.ram_monitor = RAMMonitor()
        self.disk_monitor = DiskMonitor()
        self.battery_monitor = BatteryMonitor()
        self.network_monitor = NetworkMonitor()
        self.volume_controller = VolumeController()
        self.brightness_controller = BrightnessController()

    def get_system_info(self) -> dict[str, str]:
        """Return operating system, processor, RAM, and Python details."""
        return self.system_info.get_system_info()

    def get_cpu_usage(self) -> str:
        """Return CPU usage."""
        return self.cpu_monitor.get_cpu_usage()

    def get_ram_usage(self) -> str:
        """Return RAM usage."""
        return self.ram_monitor.get_ram_usage()

    def get_disk_usage(self) -> str:
        """Return disk usage."""
        return self.disk_monitor.get_disk_usage()

    def get_battery(self) -> str:
        """Return battery status."""
        return self.battery_monitor.get_battery()

    def get_network_status(self) -> str:
        """Return network status."""
        return self.network_monitor.get_network_status()

    def set_volume(self, percent: int) -> tuple[bool, str]:
        """Set Windows volume."""
        if not is_valid_percent(percent):
            return False, "Volume must be between 0 and 100 percent."
        return self.volume_controller.set_volume(percent)

    def get_volume(self) -> int | None:
        """Return Windows volume."""
        return self.volume_controller.get_volume()

    def set_brightness(self, percent: int) -> tuple[bool, str]:
        """Set screen brightness."""
        if not is_valid_percent(percent):
            return False, "Brightness must be between 0 and 100 percent."
        return self.brightness_controller.set_brightness(percent)

    def get_brightness(self) -> int | None:
        """Return screen brightness."""
        return self.brightness_controller.get_brightness()
