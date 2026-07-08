"""Folder opening support for HI ROLEX automation."""

from __future__ import annotations

from pathlib import Path
import subprocess


class FolderManager:
    """Opens safe user folders and explicit folder paths."""

    def open_folder(self, path: str) -> tuple[bool, str]:
        """Open a known folder alias or explicit folder path."""
        folder_path = self._resolve_folder_path(path)
        if not folder_path.exists() or not folder_path.is_dir():
            return False, f"Folder not found: {folder_path}"

        try:
            subprocess.Popen(["explorer", str(folder_path)])
            return True, f"Opened folder: {folder_path}"
        except Exception as error:
            return False, f"Could not open folder: {error}"

    def _resolve_folder_path(self, path: str) -> Path:
        """Resolve known folder names to Windows user folders."""
        home = Path.home()
        aliases = {
            "downloads": home / "Downloads",
            "documents": home / "Documents",
            "desktop": home / "Desktop",
        }
        return aliases.get(path.casefold().strip(), Path(path).expanduser())
