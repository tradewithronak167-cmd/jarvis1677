"""Local Windows file management for HI ROLEX."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from utils.logger import get_logger
from utils.validators import is_safe_path


class FileManager:
    """Performs safe local file and folder operations."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def create_file(self, path: str) -> tuple[bool, str]:
        """Create an empty file if it does not already exist."""
        if not is_safe_path(path):
            return False, "Unsafe or invalid file path."
        file_path = self._resolve_path(path)
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=False)
            return True, f"Created file: {file_path}"
        except FileExistsError:
            return False, f"File already exists: {file_path}"
        except Exception as error:
            self.logger.error("Create file failed: %s", error)
            return False, f"Could not create file: {error}"

    def create_folder(self, path: str) -> tuple[bool, str]:
        """Create a folder if it does not already exist."""
        if not is_safe_path(path):
            return False, "Unsafe or invalid folder path."
        folder_path = self._resolve_path(path)
        try:
            folder_path.mkdir(parents=True, exist_ok=False)
            return True, f"Created folder: {folder_path}"
        except FileExistsError:
            return False, f"Folder already exists: {folder_path}"
        except Exception as error:
            self.logger.error("Create folder failed: %s", error)
            return False, f"Could not create folder: {error}"

    def delete_file(self, path: str) -> tuple[bool, str]:
        """Delete a file after the caller has confirmed the action."""
        if not is_safe_path(path):
            return False, "Unsafe or invalid file path."
        file_path = self._resolve_path(path)
        try:
            if not file_path.is_file():
                return False, f"File not found: {file_path}"
            file_path.unlink()
            return True, f"Deleted file: {file_path}"
        except Exception as error:
            return False, f"Could not delete file: {error}"

    def delete_folder(self, path: str) -> tuple[bool, str]:
        """Delete a folder after the caller has confirmed the action."""
        if not is_safe_path(path):
            return False, "Unsafe or invalid folder path."
        folder_path = self._resolve_path(path)
        try:
            if not folder_path.is_dir():
                return False, f"Folder not found: {folder_path}"
            shutil.rmtree(folder_path)
            return True, f"Deleted folder: {folder_path}"
        except Exception as error:
            return False, f"Could not delete folder: {error}"

    def rename(self, source: str, destination: str) -> tuple[bool, str]:
        """Rename or move a file/folder to a new destination name."""
        source_path = self._resolve_path(source)
        destination_path = self._resolve_path(destination)
        try:
            if not source_path.exists():
                return False, f"Source not found: {source_path}"
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.rename(destination_path)
            return True, f"Renamed {source_path} to {destination_path}"
        except Exception as error:
            return False, f"Could not rename: {error}"

    def copy(self, source: str, destination: str) -> tuple[bool, str]:
        """Copy a file or folder."""
        source_path = self._resolve_path(source)
        destination_path = self._resolve_path(destination)
        try:
            if not source_path.exists():
                return False, f"Source not found: {source_path}"
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.is_dir():
                shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, destination_path)
            return True, f"Copied {source_path} to {destination_path}"
        except Exception as error:
            return False, f"Could not copy: {error}"

    def move(self, source: str, destination: str) -> tuple[bool, str]:
        """Move a file or folder."""
        source_path = self._resolve_path(source)
        destination_path = self._resolve_path(destination)
        try:
            if not source_path.exists():
                return False, f"Source not found: {source_path}"
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(destination_path))
            return True, f"Moved {source_path} to {destination_path}"
        except Exception as error:
            return False, f"Could not move: {error}"

    def open_file(self, path: str) -> tuple[bool, str]:
        """Open a file using the default Windows application."""
        file_path = self._resolve_path(path)
        try:
            if not file_path.is_file():
                return False, f"File not found: {file_path}"
            os.startfile(file_path)
            return True, f"Opened file: {file_path}"
        except Exception as error:
            return False, f"Could not open file: {error}"

    def open_folder(self, path: str) -> tuple[bool, str]:
        """Open a folder in Windows File Explorer."""
        folder_path = self._resolve_path(path)
        try:
            if not folder_path.is_dir():
                return False, f"Folder not found: {folder_path}"
            os.startfile(folder_path)
            return True, f"Opened folder: {folder_path}"
        except Exception as error:
            return False, f"Could not open folder: {error}"

    def exists(self, path: str) -> bool:
        """Return True if a file or folder exists."""
        return self._resolve_path(path).exists()

    def _resolve_path(self, path: str) -> Path:
        """Resolve relative paths under the user's Documents folder."""
        raw_path = Path(path.strip()).expanduser()
        if raw_path.is_absolute():
            return raw_path
        return Path.home() / "Documents" / raw_path
