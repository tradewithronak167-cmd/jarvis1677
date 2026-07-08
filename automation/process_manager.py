"""Process helpers for HI ROLEX automation."""

from __future__ import annotations

import subprocess


class ProcessManager:
    """Provides simple Windows process lookup helpers."""

    def is_process_running(self, process_name: str) -> bool:
        """Return True when a process appears in the Windows task list."""
        try:
            completed_process = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            return False

        return process_name.casefold() in completed_process.stdout.casefold()
