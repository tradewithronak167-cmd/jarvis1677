"""HI ROLEX project health check."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.app_paths import CONFIG_DIR, DATA_DIR, LOG_DIR, MEMORY_DB_PATH, SETTINGS_PATH


class HealthCheck:
    """Runs non-destructive project checks."""

    REQUIRED_FOLDERS: tuple[str, ...] = (
        "ai",
        "assistant",
        "automation",
        "config",
        "data",
        "gui",
        "hardware",
        "language",
        "memory",
        "speech",
        "utils",
        "wakeword",
    )
    REQUIRED_FILES: tuple[str, ...] = (
        "app.py",
        "requirements.txt",
        "config/settings.json",
        "gui/main_window.py",
    )
    LANGUAGE_FILES: tuple[str, ...] = (
        "english.json",
        "tamil.json",
        "hindi.json",
        "telugu.json",
        "malayalam.json",
        "kannada.json",
    )
    REQUIRED_PACKAGES: tuple[str, ...] = (
        "customtkinter",
        "requests",
        "dotenv",
        "google.generativeai",
        "psutil",
        "pyttsx3",
        "pyaudio",
        "sounddevice",
        "speech_recognition",
    )

    def __init__(self) -> None:
        self.results: list[tuple[str, str, str]] = []

    def run(self) -> int:
        """Run all checks and print a report."""
        print("HI ROLEX Health Check")
        self.check_python_version()
        self.check_required_folders()
        self.check_required_files()
        self.check_settings()
        self.check_language_files()
        self.check_memory_database()
        self.check_env()
        self.check_ollama()
        self.check_packages()
        self.check_safety()
        self.print_results()
        return 0

    def check_python_version(self) -> None:
        """Check Python version."""
        version_ok = sys.version_info >= (3, 12)
        self.add_result("OK" if version_ok else "WARN", "Python version", sys.version.split()[0])

    def check_required_folders(self) -> None:
        """Check required folders."""
        for folder in self.REQUIRED_FOLDERS:
            path = PROJECT_ROOT / folder
            self.add_result("OK" if path.is_dir() else "WARN", f"Folder {folder}", str(path))

    def check_required_files(self) -> None:
        """Check required files."""
        for filename in self.REQUIRED_FILES:
            path = PROJECT_ROOT / filename
            self.add_result("OK" if path.is_file() else "WARN", f"File {filename}", str(path))

    def check_settings(self) -> None:
        """Check settings JSON."""
        try:
            data: Any = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            ok = isinstance(data, dict)
            self.add_result("OK" if ok else "WARN", "Settings file", "valid JSON object")
        except Exception as error:
            self.add_result("WARN", "Settings file", str(error))

    def check_language_files(self) -> None:
        """Check language JSON files exist and load."""
        for filename in self.LANGUAGE_FILES:
            path = PROJECT_ROOT / "language" / filename
            try:
                json.loads(path.read_text(encoding="utf-8"))
                self.add_result("OK", f"Language {filename}", "valid")
            except Exception as error:
                self.add_result("WARN", f"Language {filename}", str(error))

    def check_memory_database(self) -> None:
        """Check memory database can be opened."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(MEMORY_DB_PATH) as connection:
                connection.execute("SELECT 1")
            self.add_result("OK", "Memory database", str(MEMORY_DB_PATH))
        except Exception as error:
            self.add_result("WARN", "Memory database", str(error))

    def check_env(self) -> None:
        """Check .env and Gemini key presence."""
        env_path = PROJECT_ROOT / ".env"
        if not env_path.is_file():
            self.add_result("WARN", ".env file", "missing")
            return

        self.add_result("OK", ".env file", "exists")
        value = self._read_env_value(env_path, "GEMINI_API_KEY")
        if value:
            self.add_result("OK", "Gemini API key", "configured")
        else:
            self.add_result("WARN", "Gemini API key", "missing")

    def check_ollama(self) -> None:
        """Check Ollama local server."""
        try:
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            self.add_result(
                "OK" if response.status_code == 200 else "WARN",
                "Ollama server",
                f"HTTP {response.status_code}",
            )
        except Exception:
            self.add_result("WARN", "Ollama server", "not running")

    def check_packages(self) -> None:
        """Check important imports."""
        for package in self.REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
                self.add_result("OK", f"Package {package}", "installed")
            except Exception:
                self.add_result("WARN", f"Package {package}", "missing")

    def check_safety(self) -> None:
        """Check that dangerous operations are not exposed as supported commands."""
        try:
            from assistant.command_router import CommandRouter

            result = CommandRouter().handle_user_input("format drive")
            refused = not result.success and "cannot" in result.message.casefold()
            self.add_result("OK" if refused else "WARN", "Dangerous operations", "blocked")
        except Exception as error:
            self.add_result("WARN", "Dangerous operations", str(error))

    def add_result(self, status: str, name: str, detail: str) -> None:
        """Store one check result."""
        self.results.append((status, name, detail))

    def print_results(self) -> None:
        """Print all check results."""
        for status, name, detail in self.results:
            print(f"[{status}] {name}: {detail}")

    def _read_env_value(self, env_path: Path, key: str) -> str:
        """Read one .env value without printing secrets."""
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
        except OSError:
            return ""
        return ""


def main() -> int:
    """Run the health check."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        return HealthCheck().run()
    except Exception as error:
        print("HI ROLEX Health Check")
        print(f"[WARN] Health check recovered from an error: {error}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
