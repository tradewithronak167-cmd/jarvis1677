"""Professional rule-based automation engine for HI ROLEX."""

from __future__ import annotations

from dataclasses import dataclass

from automation.app_launcher import AppLauncher
from automation.browser_manager import BrowserManager
from automation.command_history import CommandHistory
from automation.command_parser import CommandParser
from automation.file_manager import FileManager
from automation.folder_manager import FolderManager
from automation.operation_history import OperationHistory


@dataclass(frozen=True)
class AutomationResult:
    """Result object returned after executing an automation command."""

    user_command: str
    assistant_action: str
    execution_result: str
    success: bool


class AutomationManager:
    """Coordinates rule-based parsing and Windows automation actions."""

    def __init__(self) -> None:
        self.command_parser = CommandParser()
        self.app_launcher = AppLauncher()
        self.browser_manager = BrowserManager()
        self.file_manager = FileManager()
        self.folder_manager = FolderManager()
        self.command_history = CommandHistory()
        self.operation_history = OperationHistory()

    def execute_command(self, command: str) -> AutomationResult:
        """Parse and execute a supported command."""
        self.command_history.add_command(command)
        parsed_command = self.command_parser.parse(command)

        if parsed_command.action == "open_application":
            success, result = self.open_application(parsed_command.target)
        elif parsed_command.action == "close_application":
            success, result = self.close_application(parsed_command.target)
        elif parsed_command.action == "open_website":
            success, result = self.open_website(parsed_command.target)
        elif parsed_command.action == "google_search":
            success, result = self.google_search(parsed_command.target)
        elif parsed_command.action == "open_folder":
            success, result = self.open_folder(parsed_command.target)
        elif parsed_command.action == "open_local_folder":
            success, result = self.file_manager.open_folder(parsed_command.target)
        elif parsed_command.action == "open_file":
            success, result = self.file_manager.open_file(parsed_command.target)
        elif parsed_command.action == "create_file":
            success, result = self.file_manager.create_file(parsed_command.target)
            self.operation_history.add_operation(parsed_command.assistant_action, result)
        elif parsed_command.action == "create_folder":
            success, result = self.file_manager.create_folder(parsed_command.target)
            self.operation_history.add_operation(parsed_command.assistant_action, result)
        elif parsed_command.action == "rename":
            success, result = self.file_manager.rename(
                parsed_command.target,
                parsed_command.destination,
            )
            self.operation_history.add_operation(parsed_command.assistant_action, result)
        elif parsed_command.action == "copy":
            success, result = self.file_manager.copy(
                parsed_command.target,
                parsed_command.destination,
            )
            self.operation_history.add_operation(parsed_command.assistant_action, result)
        elif parsed_command.action == "move":
            success, result = self.file_manager.move(
                parsed_command.target,
                parsed_command.destination,
            )
            self.operation_history.add_operation(parsed_command.assistant_action, result)
        elif parsed_command.action == "delete_requires_confirmation":
            success = False
            result = (
                "Delete commands require confirmation. "
                "Please use the File Manager window to delete files or folders."
            )
        else:
            success = False
            result = "I do not know how to do that yet."

        return AutomationResult(
            user_command=command,
            assistant_action=parsed_command.assistant_action,
            execution_result=result,
            success=success,
        )

    def open_application(self, name: str) -> tuple[bool, str]:
        """Open a Windows application by supported name."""
        return self.app_launcher.open_application(name)

    def close_application(self, name: str) -> tuple[bool, str]:
        """Close a Windows application by supported name."""
        return self.app_launcher.close_application(name)

    def open_website(self, url: str) -> tuple[bool, str]:
        """Open a website in the default browser."""
        return self.browser_manager.open_website(url)

    def google_search(self, query: str) -> tuple[bool, str]:
        """Open a Google search in the default browser."""
        return self.browser_manager.google_search(query)

    def open_folder(self, path: str) -> tuple[bool, str]:
        """Open a known folder or explicit folder path."""
        return self.folder_manager.open_folder(path)
