"""Central project paths for HI ROLEX.

The app can run in two modes:
- normal Python mode from the project folder
- bundled PyInstaller mode from a release folder

Writable files live beside the executable in bundled mode, while bundled
defaults can still be copied from PyInstaller's temporary resource folder.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


IS_FROZEN: bool = bool(getattr(sys, "frozen", False))
RESOURCE_ROOT: Path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PROJECT_ROOT: Path = Path(sys.executable).resolve().parent if IS_FROZEN else RESOURCE_ROOT
DATA_DIR: Path = PROJECT_ROOT / "data"
CONFIG_DIR: Path = PROJECT_ROOT / "config"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
LANGUAGE_DIR: Path = PROJECT_ROOT / "language"
LOG_DIR: Path = DATA_DIR / "logs"
MEMORY_DB_PATH: Path = DATA_DIR / "hi_rolex_memory.db"
SETTINGS_PATH: Path = CONFIG_DIR / "settings.json"


def ensure_required_directories() -> None:
    """Create folders the app needs at runtime."""
    if IS_FROZEN:
        _copy_bundled_defaults()

    for path in (DATA_DIR, CONFIG_DIR, ASSETS_DIR, LANGUAGE_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def bundled_resource_path(relative_path: str) -> Path:
    """Return a resource path from the bundled app or project root."""
    return RESOURCE_ROOT / relative_path


def _copy_bundled_defaults() -> None:
    """Copy bundled runtime folders beside the executable on first launch."""
    for folder_name in ("assets", "config", "language", "data"):
        source = RESOURCE_ROOT / folder_name
        target = PROJECT_ROOT / folder_name
        if source.exists() and not target.exists():
            try:
                shutil.copytree(source, target)
            except OSError:
                target.mkdir(parents=True, exist_ok=True)
