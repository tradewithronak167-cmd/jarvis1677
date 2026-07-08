"""System information for HI ROLEX."""

from __future__ import annotations

import platform
import sys

from hardware.ram_monitor import RAMMonitor


class SystemInfo:
    """Provides static operating system and Python information."""

    def get_system_info(self) -> dict[str, str]:
        """Return useful system details for the Hardware window."""
        return {
            "operating_system": f"{platform.system()} {platform.release()}",
            "processor": platform.processor() or "Unavailable",
            "ram_size": RAMMonitor().get_total_ram(),
            "python_version": sys.version.split()[0],
        }
