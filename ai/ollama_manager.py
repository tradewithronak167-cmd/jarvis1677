"""Ollama local server client for HI ROLEX."""

from __future__ import annotations

import time
from typing import Any

from utils.logger import get_logger


class OllamaManager:
    """Communicates with the local Ollama HTTP API."""

    BASE_URL: str = "http://localhost:11434"
    CACHE_SECONDS: float = 15.0

    def __init__(self) -> None:
        self.logger = get_logger()
        self._last_checked_at = 0.0
        self._last_running = False

    def check_ollama_running(self) -> bool:
        """Return True when the Ollama local server responds."""
        now = time.monotonic()
        if now - self._last_checked_at < self.CACHE_SECONDS:
            return self._last_running

        try:
            import requests

            response = requests.get(f"{self.BASE_URL}/api/tags", timeout=0.8)
            self._last_running = response.status_code == 200
        except Exception as error:
            self.logger.error("Ollama availability check failed: %s", error)
            self._last_running = False

        self._last_checked_at = now
        return self._last_running

    def list_models(self) -> list[str]:
        """Return locally installed Ollama model names."""
        try:
            import requests

            response = requests.get(f"{self.BASE_URL}/api/tags", timeout=4)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            models = data.get("models", [])
            return [
                str(model.get("name", ""))
                for model in models
                if isinstance(model, dict) and model.get("name")
            ]
        except Exception as error:
            self.logger.error("Ollama list models failed: %s", error)
            return []

    def pull_model(self, model_name: str) -> str:
        """Ask Ollama to pull a model by name."""
        try:
            import requests

            response = requests.post(
                f"{self.BASE_URL}/api/pull",
                json={"name": model_name},
                timeout=120,
            )
            response.raise_for_status()
            return f"Ollama model pull requested: {model_name}"
        except requests.Timeout:
            return f"Ollama model pull timed out: {model_name}"
        except Exception as error:
            self.logger.error("Ollama pull failed: %s", error)
            return f"Could not pull Ollama model: {error}"

    def generate(self, model_name: str, prompt: str) -> str:
        """Generate a response from a local Ollama model."""
        try:
            import requests

            response = requests.post(
                f"{self.BASE_URL}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 500,
                    },
                },
                timeout=60,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return str(data.get("response", "")).strip()
        except requests.Timeout:
            return "Offline AI timed out while waiting for Ollama."
        except Exception as error:
            self.logger.error("Ollama generate failed: %s", error)
            return f"Offline AI error: {error}"
