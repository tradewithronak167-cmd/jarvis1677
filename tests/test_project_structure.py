"""Basic tests for the Day 1 project scaffold."""

from pathlib import Path


def test_expected_project_folders_exist() -> None:
    """Verify the main modular folders are present."""
    project_root = Path(__file__).resolve().parents[1]
    expected_folders = [
        "gui",
        "config",
        "speech",
        "wakeword",
        "ai",
        "automation",
        "hardware",
        "memory",
        "language",
        "plugins",
        "utils",
        "assets",
        "data",
        "tests",
    ]

    for folder_name in expected_folders:
        assert (project_root / folder_name).is_dir()
