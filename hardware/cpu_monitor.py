"""CPU monitoring for HI ROLEX."""

from __future__ import annotations


class CPUMonitor:
    """Reads CPU usage from the local Windows machine."""

    def get_cpu_usage(self) -> str:
        """Return current CPU usage as display text."""
        try:
            import psutil

            return f"{psutil.cpu_percent(interval=0.1):.0f}%"
        except Exception:
            return "Unavailable"
