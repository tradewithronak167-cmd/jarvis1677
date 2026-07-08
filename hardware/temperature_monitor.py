"""Temperature monitoring for HI ROLEX."""

from __future__ import annotations


class TemperatureMonitor:
    """Reads temperature sensors when available."""

    def get_temperature(self) -> str:
        """Return CPU temperature if the OS exposes it."""
        try:
            import psutil

            temperatures = psutil.sensors_temperatures()
            for sensor_entries in temperatures.values():
                if sensor_entries:
                    return f"{sensor_entries[0].current:.1f} C"
            return "Unavailable"
        except Exception:
            return "Unavailable"
