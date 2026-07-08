"""Rule-based intent classifier for HI ROLEX."""

from __future__ import annotations

import re

from assistant.command_models import CommandIntent


class IntentClassifier:
    """Classifies English commands into safe project intent categories."""

    APP_ALIASES: dict[str, str] = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "notepad": "notepad",
        "calculator": "calculator",
        "vscode": "vscode",
        "visual studio code": "vscode",
        "paint": "paint",
        "command prompt": "command prompt",
        "powershell": "powershell",
        "file explorer": "file explorer",
        "task manager": "task manager",
        "settings": "settings",
        "windows settings": "settings",
        "control panel": "control panel",
        "device manager": "device manager",
        "system information": "system information",
    }
    FOLDER_ALIASES: dict[str, str] = {
        "downloads": "downloads",
        "documents": "documents",
        "desktop": "desktop",
    }
    WEBSITE_ALIASES: dict[str, str] = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com",
    }
    DANGEROUS_TERMS: tuple[str, ...] = (
        "shutdown",
        "restart",
        "sleep",
        "hibernate",
        "format drive",
        "format disk",
        "registry",
        "regedit",
        "bios",
        "disable antivirus",
        "delete system32",
        "powershell command",
        "cmd command",
        "terminal command",
        "run script",
    )

    def classify(self, text: str) -> CommandIntent:
        """Classify one command step."""
        original_text = text.strip()
        normalized = self._normalize(original_text)

        if any(term in normalized for term in self.DANGEROUS_TERMS):
            return CommandIntent("unknown", original_text, parameters={"dangerous": "true"})

        if normalized.startswith("remember my name is "):
            value = original_text[len("remember my name is ") :].strip()
            return CommandIntent("memory_store", original_text, "name", value)

        if normalized.startswith("remember that "):
            value = original_text[len("remember that ") :].strip()
            return CommandIntent("memory_store", original_text, "memory", value)

        if normalized == "what do you remember about me":
            return CommandIntent("memory_query", original_text)

        if normalized == "forget my name":
            return CommandIntent(
                "memory_delete",
                original_text,
                "name",
                requires_confirmation=True,
            )

        if normalized.startswith("search google for "):
            query = original_text[len("search google for ") :].strip()
            return CommandIntent("google_search", original_text, query)

        if normalized.startswith("open "):
            target = normalized.removeprefix("open ").strip()
            original_target = original_text[len("open ") :].strip()
            if target in self.APP_ALIASES:
                return CommandIntent("open_app", original_text, self.APP_ALIASES[target])
            if target in self.FOLDER_ALIASES:
                return CommandIntent("open_folder", original_text, self.FOLDER_ALIASES[target])
            if target in self.WEBSITE_ALIASES:
                return CommandIntent("open_website", original_text, self.WEBSITE_ALIASES[target])
            if target.startswith("folder "):
                return CommandIntent("open_folder", original_text, original_target[7:].strip())
            if self._looks_like_url(target):
                return CommandIntent("open_website", original_text, original_target)

        if normalized.startswith("close "):
            target = normalized.removeprefix("close ").strip()
            if target in self.APP_ALIASES:
                return CommandIntent(
                    "close_app",
                    original_text,
                    self.APP_ALIASES[target],
                    requires_confirmation=True,
                )

        if normalized.startswith("set volume to "):
            percent = self._extract_percent(normalized)
            return CommandIntent("hardware_control", original_text, "volume", percent)

        if normalized.startswith("set brightness to "):
            percent = self._extract_percent(normalized)
            return CommandIntent("hardware_control", original_text, "brightness", percent)

        if "battery" in normalized:
            return CommandIntent("hardware_status", original_text, "battery")
        if "cpu" in normalized:
            return CommandIntent("hardware_status", original_text, "cpu")
        if "ram" in normalized or "memory usage" in normalized:
            return CommandIntent("hardware_status", original_text, "ram")
        if "disk" in normalized:
            return CommandIntent("hardware_status", original_text, "disk")
        if "network" in normalized or "internet status" in normalized:
            return CommandIntent("hardware_status", original_text, "network")

        file_intent = self._classify_file_operation(original_text, normalized)
        if file_intent is not None:
            return file_intent

        return CommandIntent("ai_chat", original_text, original_text)

    def _classify_file_operation(
        self,
        original_text: str,
        normalized: str,
    ) -> CommandIntent | None:
        """Classify supported file operations."""
        patterns = {
            "create file ": "create_file",
            "create folder ": "create_folder",
            "delete file ": "delete_file",
            "delete folder ": "delete_folder",
        }
        for prefix, operation in patterns.items():
            if normalized.startswith(prefix):
                target = original_text[len(prefix) :].strip()
                return CommandIntent(
                    "file_operation",
                    original_text,
                    target,
                    parameters={"operation": operation},
                    requires_confirmation=True,
                )

        for prefix, operation in {
            "rename file ": "rename",
            "rename folder ": "rename",
            "copy file ": "copy",
            "copy folder ": "copy",
            "move file ": "move",
            "move folder ": "move",
        }.items():
            if normalized.startswith(prefix):
                body = original_text[len(prefix) :].strip()
                source, destination = self._split_source_destination(body)
                return CommandIntent(
                    "file_operation",
                    original_text,
                    source,
                    destination,
                    {"operation": operation},
                    True,
                )
        return None

    def _split_source_destination(self, body: str) -> tuple[str, str]:
        """Split source and destination around ' to '."""
        lower_body = body.casefold()
        if " to " not in lower_body:
            return body, ""
        index = lower_body.index(" to ")
        return body[:index].strip(), body[index + 4 :].strip()

    def _extract_percent(self, text: str) -> str:
        """Extract a percentage integer from text."""
        match = re.search(r"(\d{1,3})", text)
        if match is None:
            return ""
        return str(max(0, min(100, int(match.group(1)))))

    def _looks_like_url(self, text: str) -> bool:
        """Return True when a target resembles a URL."""
        return text.startswith(("http://", "https://")) or "." in text

    def _normalize(self, text: str) -> str:
        """Normalize command text for matching."""
        return " ".join(text.casefold().strip().split())
