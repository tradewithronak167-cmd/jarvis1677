"""Task execution through registered HI ROLEX project managers."""

from __future__ import annotations

from ai.ai_manager import AIManager
from assistant.command_models import CommandResult, PlannedAction, TaskPlan
from automation.automation_manager import AutomationManager
from automation.file_manager import FileManager
from hardware.hardware_manager import HardwareManager
from memory.memory_manager import MemoryManager
from memory.profile_manager import ProfileManager


class TaskExecutor:
    """Executes planned actions using only safe project modules."""

    def __init__(
        self,
        automation_manager: AutomationManager | None = None,
        file_manager: FileManager | None = None,
        hardware_manager: HardwareManager | None = None,
        memory_manager: MemoryManager | None = None,
        profile_manager: ProfileManager | None = None,
        ai_manager: AIManager | None = None,
    ) -> None:
        self.automation_manager = automation_manager or AutomationManager()
        self.file_manager = file_manager or FileManager()
        self.hardware_manager = hardware_manager or HardwareManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.profile_manager = profile_manager or ProfileManager()
        self.ai_manager = ai_manager or AIManager()

    def execute_plan(self, plan: TaskPlan) -> list[CommandResult]:
        """Execute every action in order."""
        return [self.execute_action(action) for action in plan.actions]

    def execute_action(self, action: PlannedAction) -> CommandResult:
        """Execute one planned action."""
        intent = action.intent
        try:
            if intent.category == "open_app":
                success, message = self.automation_manager.open_application(intent.target)
                return self._result(success, message, action.description)
            if intent.category == "close_app":
                success, message = self.automation_manager.close_application(intent.target)
                return self._result(success, message, action.description)
            if intent.category == "open_website":
                success, message = self.automation_manager.open_website(intent.target)
                return self._result(success, message, action.description)
            if intent.category == "google_search":
                success, message = self.automation_manager.google_search(intent.target)
                return self._result(success, message, action.description)
            if intent.category == "open_folder":
                success, message = self.automation_manager.open_folder(intent.target)
                return self._result(success, message, action.description)
            if intent.category == "file_operation":
                return self._execute_file_operation(action)
            if intent.category == "hardware_status":
                return self._execute_hardware_status(action)
            if intent.category == "hardware_control":
                return self._execute_hardware_control(action)
            if intent.category == "memory_store":
                return self._execute_memory_store(action)
            if intent.category == "memory_query":
                return self._execute_memory_query(action)
            if intent.category == "memory_delete":
                return self._execute_memory_delete(action)
            if intent.category == "ai_chat":
                message = self.ai_manager.ask(intent.raw_text)
                return self._result(True, message, action.description)

            return self._result(
                False,
                "I cannot perform that request safely.",
                action.description,
            )
        except Exception as error:
            return self._result(False, f"Action failed safely: {error}", action.description)

    def _execute_file_operation(self, action: PlannedAction) -> CommandResult:
        """Execute a confirmed file operation."""
        intent = action.intent
        operation = intent.parameters.get("operation", "")
        if operation == "create_file":
            success, message = self.file_manager.create_file(intent.target)
        elif operation == "create_folder":
            success, message = self.file_manager.create_folder(intent.target)
        elif operation == "delete_file":
            success, message = self.file_manager.delete_file(intent.target)
        elif operation == "delete_folder":
            success, message = self.file_manager.delete_folder(intent.target)
        elif operation == "rename":
            success, message = self.file_manager.rename(intent.target, intent.destination)
        elif operation == "copy":
            success, message = self.file_manager.copy(intent.target, intent.destination)
        elif operation == "move":
            success, message = self.file_manager.move(intent.target, intent.destination)
        else:
            success, message = False, "Unsupported file operation."
        return self._result(success, message, action.description)

    def _execute_hardware_status(self, action: PlannedAction) -> CommandResult:
        """Read safe hardware status."""
        target = action.intent.target
        if target == "battery":
            message = f"Battery: {self.hardware_manager.get_battery()}"
        elif target == "cpu":
            message = f"CPU Usage: {self.hardware_manager.get_cpu_usage()}"
        elif target == "ram":
            message = f"RAM Usage: {self.hardware_manager.get_ram_usage()}"
        elif target == "disk":
            message = f"Disk Usage: {self.hardware_manager.get_disk_usage()}"
        elif target == "network":
            message = f"Network: {self.hardware_manager.get_network_status()}"
        else:
            message = "Hardware status is unavailable."
        return self._result(True, message, action.description)

    def _execute_hardware_control(self, action: PlannedAction) -> CommandResult:
        """Execute safe hardware controls."""
        target = action.intent.target
        percent = int(action.intent.destination or "0")
        if target == "volume":
            success, message = self.hardware_manager.set_volume(percent)
        elif target == "brightness":
            success, message = self.hardware_manager.set_brightness(percent)
        else:
            success, message = False, "Unsupported hardware control."
        return self._result(success, message, action.description)

    def _execute_memory_store(self, action: PlannedAction) -> CommandResult:
        """Store explicit safe memories."""
        intent = action.intent
        if intent.target == "name":
            if not self.profile_manager.set_profile_value("display_name", intent.destination):
                return self._result(False, "I cannot safely save that memory.", action.description)
            self.memory_manager.add_memory("profile", "name", intent.destination)
            return self._result(True, f"I will remember your name is {intent.destination}.", action.description)

        key = self._memory_key_from_text(intent.destination)
        if self.memory_manager.add_memory("user", key, intent.destination):
            return self._result(True, "I saved that memory.", action.description)
        return self._result(False, "I cannot safely save that memory.", action.description)

    def _execute_memory_query(self, action: PlannedAction) -> CommandResult:
        """Read safe saved memories."""
        lines: list[str] = []
        for key, value in self.profile_manager.get_profile().items():
            if value and self.memory_manager.is_safe_to_store(value):
                lines.append(f"{key}: {value}")
        for memory in self.memory_manager.get_all_memories()[:10]:
            text = f"{memory.key}: {memory.value}"
            if self.memory_manager.is_safe_to_store(text):
                lines.append(text)
        message = "I do not have any saved memories yet." if not lines else "\n".join(lines[:10])
        return self._result(True, message, action.description)

    def _execute_memory_delete(self, action: PlannedAction) -> CommandResult:
        """Delete supported memory items after confirmation."""
        if action.intent.target == "name":
            deleted_any = False
            for memory in self.memory_manager.search_memories("name"):
                deleted_any = self.memory_manager.delete_memory(memory.memory_id) or deleted_any
            self.profile_manager.set_profile_value("display_name", "")
            message = "I forgot your saved name." if deleted_any else "I did not have your name saved."
            return self._result(True, message, action.description)
        return self._result(False, "Unsupported memory delete request.", action.description)

    def _memory_key_from_text(self, text: str) -> str:
        """Create a simple key from remembered text."""
        words = [word.strip(".,!?;:").casefold() for word in text.split()]
        useful_words = [word for word in words if word and word not in {"i", "my", "that"}]
        return "_".join(useful_words[:4]) or "memory"

    def _result(self, success: bool, message: str, details: str) -> CommandResult:
        """Create a CommandResult."""
        return CommandResult(success=success, message=message, action_details=details)
