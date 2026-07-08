"""Disk monitoring for HI ROLEX."""

from __future__ import annotations

from pathlib import Path


class DiskMonitor:
    """Reads disk usage for the Windows system drive."""

    def get_disk_usage(self) -> str:
        """Return system drive usage as display text."""
        try:
            import psutil

            usage = psutil.disk_usage(Path.home().anchor)
            used_gb = usage.used / (1024**3)
            total_gb = usage.total / (1024**3)
            return f"{usage.percent:.0f}% ({used_gb:.1f} GB / {total_gb:.1f} GB)"
        except Exception:
            return "Unavailable"
