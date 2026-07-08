"""Battery monitoring for HI ROLEX."""

from __future__ import annotations


class BatteryMonitor:
    """Reads battery status when Windows exposes a battery device."""

    def get_battery(self) -> str:
        """Return battery status as display text."""
        try:
            import psutil

            battery = psutil.sensors_battery()
            if battery is None:
                return "No battery detected"
            charging_text = "Charging" if battery.power_plugged else "Discharging"
            return f"{battery.percent:.0f}% ({charging_text})"
        except Exception:
            return "Unavailable"
