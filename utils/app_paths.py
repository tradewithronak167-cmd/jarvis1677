"""Central project paths for HI ROLEX."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = PROJECT_ROOT / "data"
CONFIG_DIR: Path = PROJECT_ROOT / "config"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
LOG_DIR: Path = DATA_DIR / "logs"
MEMORY_DB_PATH: Path = DATA_DIR / "hi_rolex_memory.db"
SETTINGS_PATH: Path = CONFIG_DIR / "settings.json"


def ensure_required_directories() -> None:
    """Create folders the app needs at runtime."""
    for path in (DATA_DIR, CONFIG_DIR, ASSETS_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)
