"""RAM monitoring for HI ROLEX."""

from __future__ import annotations


class RAMMonitor:
    """Reads memory usage and installed RAM."""

    def get_ram_usage(self) -> str:
        """Return current RAM usage as display text."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            return f"{memory.percent:.0f}% ({used_gb:.1f} GB / {total_gb:.1f} GB)"
        except Exception:
            return "Unavailable"

    def get_total_ram(self) -> str:
        """Return total installed RAM as display text."""
        try:
            import psutil

            total_gb = psutil.virtual_memory().total / (1024**3)
            return f"{total_gb:.1f} GB"
        except Exception:
            return "Unavailable"
