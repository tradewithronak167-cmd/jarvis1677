"""Rule-based command parsing for HI ROLEX automation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedCommand:
    """Structured result produced by the rule-based command parser."""

    action: str
    target: str
    assistant_action: str
    destination: str = ""


class CommandParser:
    """Parses supported automation commands without using AI."""

    APP_ALIASES: dict[str, str] = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "vscode": "vscode",
        "visual studio code": "vscode",
        "notepad": "notepad",
        "calculator": "calculator",
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
        "system info": "system information",
        "resource monitor": "resource monitor",
        "performance monitor": "performance monitor",
        "event viewer": "event viewer",
        "eventvwr": "event viewer",
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

    def parse(self, command: str) -> ParsedCommand:
        """Convert user text into a supported automation action."""
        normalized_command = self._normalize(command)

        if normalized_command.startswith("search google for "):
            query = normalized_command.removeprefix("search google for ").strip()
            return ParsedCommand("google_search", query, f"Searching Google for {query}")

        if normalized_command.startswith("create folder "):
            folder_path = command.strip()[len("create folder ") :].strip()
            return ParsedCommand("create_folder", folder_path, f"Creating folder {folder_path}")

        if normalized_command.startswith("create file "):
            file_path = command.strip()[len("create file ") :].strip()
            return ParsedCommand("create_file", file_path, f"Creating file {file_path}")

        if normalized_command.startswith("rename file ") or normalized_command.startswith(
            "rename folder "
        ):
            item_type = "file" if normalized_command.startswith("rename file ") else "folder"
            prefix = f"rename {item_type} "
            return self._parse_two_path_command(
                command,
                prefix,
                "rename",
                f"Renaming {item_type}",
            )

        if normalized_command.startswith("copy file ") or normalized_command.startswith(
            "copy folder "
        ):
            item_type = "file" if normalized_command.startswith("copy file ") else "folder"
            prefix = f"copy {item_type} "
            return self._parse_two_path_command(command, prefix, "copy", f"Copying {item_type}")

        if normalized_command.startswith("move file ") or normalized_command.startswith(
            "move folder "
        ):
            item_type = "file" if normalized_command.startswith("move file ") else "folder"
            prefix = f"move {item_type} "
            return self._parse_two_path_command(command, prefix, "move", f"Moving {item_type}")

        if normalized_command == "copy file" or normalized_command == "move file":
            return ParsedCommand(
                "unknown",
                command,
                "Please include source and destination paths",
            )

        if normalized_command.startswith("delete file "):
            file_path = command.strip()[len("delete file ") :].strip()
            return ParsedCommand(
                "delete_requires_confirmation",
                file_path,
                f"Delete requested for file {file_path}",
            )

        if normalized_command.startswith("delete folder "):
            folder_path = command.strip()[len("delete folder ") :].strip()
            return ParsedCommand(
                "delete_requires_confirmation",
                folder_path,
                f"Delete requested for folder {folder_path}",
            )

        if normalized_command.startswith("open "):
            target = normalized_command.removeprefix("open ").strip()
            original_target = command.strip()[len("open ") :].strip()
            if target.startswith("file "):
                file_path = original_target[len("file ") :].strip()
                return ParsedCommand("open_file", file_path, f"Opening file {file_path}")
            if target.startswith("folder "):
                folder_path = original_target[len("folder ") :].strip()
                return ParsedCommand(
                    "open_local_folder",
                    folder_path,
                    f"Opening folder {folder_path}",
                )
            if target in self.APP_ALIASES:
                app_name = self.APP_ALIASES[target]
                return ParsedCommand("open_application", app_name, f"Opening {target}")
            if target in self.FOLDER_ALIASES:
                folder_name = self.FOLDER_ALIASES[target]
                return ParsedCommand("open_folder", folder_name, f"Opening {target} folder")
            if target in self.WEBSITE_ALIASES:
                url = self.WEBSITE_ALIASES[target]
                return ParsedCommand("open_website", url, f"Opening {target}")
            if self._looks_like_url(target):
                return ParsedCommand("open_website", target, f"Opening {target}")
            return ParsedCommand("open_application", original_target, f"Opening {original_target}")

        if normalized_command.startswith("close "):
            target = normalized_command.removeprefix("close ").strip()
            if target in self.APP_ALIASES:
                app_name = self.APP_ALIASES[target]
                return ParsedCommand("close_application", app_name, f"Closing {target}")

        return ParsedCommand(
            "unknown",
            command,
            "Command not recognized by the rule-based automation engine",
        )

    def _normalize(self, command: str) -> str:
        """Normalize user command text for predictable matching."""
        return " ".join(command.casefold().strip().split())

    def _looks_like_url(self, text: str) -> bool:
        """Return True if the command target looks like a website URL."""
        return (
            text.startswith("http://")
            or text.startswith("https://")
            or "." in text
        )

    def _parse_two_path_command(
        self,
        original_command: str,
        prefix: str,
        action: str,
        assistant_action: str,
    ) -> ParsedCommand:
        """Parse commands that need source and destination paths."""
        command_body = original_command.strip()[len(prefix) :].strip()
        separator = " to "
        if separator not in command_body.casefold():
            return ParsedCommand(
                "unknown",
                original_command,
                "Please include source and destination paths",
            )

        lower_body = command_body.casefold()
        separator_index = lower_body.index(separator)
        source = command_body[:separator_index].strip()
        destination = command_body[separator_index + len(separator) :].strip()
        return ParsedCommand(action, source, f"{assistant_action} {source}", destination)
