"""Smart command router for HI ROLEX."""

from __future__ import annotations

import re

from assistant.command_models import CommandResult, TaskPlan
from assistant.confirmation_manager import ConfirmationManager
from assistant.intent_classifier import IntentClassifier
from assistant.task_executor import TaskExecutor
from assistant.task_planner import TaskPlanner
from automation.command_history import CommandHistory


class CommandRouter:
    """Plans, confirms, and executes safe HI ROLEX commands."""

    CONFIRM_WORDS: set[str] = {"confirm", "yes"}
    CANCEL_WORDS: set[str] = {"cancel", "no"}

    def __init__(
        self,
        task_planner: TaskPlanner | None = None,
        task_executor: TaskExecutor | None = None,
        confirmation_manager: ConfirmationManager | None = None,
        command_history: CommandHistory | None = None,
    ) -> None:
        self.task_planner = task_planner or TaskPlanner(IntentClassifier())
        self.task_executor = task_executor or TaskExecutor()
        self.confirmation_manager = confirmation_manager or ConfirmationManager()
        self.command_history = command_history or CommandHistory()

    def handle_user_input(self, text: str, source: str = "chat") -> CommandResult:
        """Route user input from chat or voice."""
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            return CommandResult(False, "Please enter a command.")

        normalized = cleaned_text.casefold()
        if normalized in self.CONFIRM_WORDS:
            return self.confirm_pending_action()
        if normalized in self.CANCEL_WORDS:
            return self.cancel_pending_action()

        plan = self.create_plan(cleaned_text)
        if self._contains_dangerous_request(plan):
            result = CommandResult(
                False,
                "I cannot perform that request safely.",
                self._format_plan(plan),
            )
            self._record_history(cleaned_text, source, plan, result)
            return result

        if plan.requires_confirmation:
            self.confirmation_manager.set_pending_plan(plan)
            result = CommandResult(
                False,
                self._confirmation_message(plan),
                self._format_plan(plan),
                True,
                plan.actions[0] if plan.actions else None,
                plan,
            )
            self._record_history(cleaned_text, source, plan, result)
            return result

        results = self.execute_plan(plan)
        result = self._combine_results(plan, results)
        self._record_history(cleaned_text, source, plan, result)
        return result

    def create_plan(self, text: str) -> TaskPlan:
        """Create a task plan for user text."""
        return self.task_planner.create_plan(text)

    def execute_plan(self, plan: TaskPlan) -> list[CommandResult]:
        """Execute a task plan."""
        return self.task_executor.execute_plan(plan)

    def confirm_pending_action(self) -> CommandResult:
        """Execute the pending plan after user confirmation."""
        plan = self.confirmation_manager.get_pending_plan()
        if plan is None:
            return CommandResult(False, "There is no pending action to confirm.")

        self.confirmation_manager.clear_pending_plan()
        results = self.execute_plan(plan)
        result = self._combine_results(plan, results)
        self._record_history("confirm", "chat", plan, result)
        return result

    def cancel_pending_action(self) -> CommandResult:
        """Cancel the pending plan."""
        plan = self.confirmation_manager.get_pending_plan()
        self.confirmation_manager.clear_pending_plan()
        if plan is None:
            return CommandResult(False, "There is no pending action to cancel.")
        return CommandResult(True, "Pending action cancelled.", self._format_plan(plan))

    def _combine_results(
        self,
        plan: TaskPlan,
        results: list[CommandResult],
    ) -> CommandResult:
        """Combine action results into one GUI-friendly result."""
        success = all(result.success for result in results)
        messages = [result.message for result in results if result.message]
        message = "\n".join(messages) or "Completed."
        return CommandResult(success, message, self._format_plan(plan))

    def _confirmation_message(self, plan: TaskPlan) -> str:
        """Create a clear confirmation message."""
        descriptions = ", ".join(action.description for action in plan.actions)
        return f"Confirmation required: {descriptions}?"

    def _format_plan(self, plan: TaskPlan) -> str:
        """Format a plan as numbered text."""
        if not plan.actions:
            return "No actions planned."
        return "\n".join(
            f"{index}. {action.description}"
            for index, action in enumerate(plan.actions, start=1)
        )

    def _contains_dangerous_request(self, plan: TaskPlan) -> bool:
        """Return True when a plan contains blocked unknown dangerous text."""
        return any(
            action.intent.category == "unknown"
            and action.intent.parameters.get("dangerous") == "true"
            for action in plan.actions
        )

    def _record_history(
        self,
        command: str,
        source: str,
        plan: TaskPlan,
        result: CommandResult,
    ) -> None:
        """Store non-sensitive command routing history."""
        self.command_history.add_command(
            command=self._safe_history_command(command),
            source=source,
            planned_actions=[action.description for action in plan.actions],
            success=result.success,
        )

    def _clean_text(self, text: str) -> str:
        """Clean raw user input."""
        return " ".join(text.strip().split())

    def _safe_history_command(self, command: str) -> str:
        """Redact sensitive-looking commands before history storage."""
        sensitive_terms = (
            "password",
            "api key",
            "apikey",
            "token",
            "pin",
            "bank",
            "card",
            "private key",
            "secret",
        )
        lowered = command.casefold()
        if any(term in lowered for term in sensitive_terms):
            return "[REDACTED SENSITIVE COMMAND]"
        if re.search(r"\b(?:\d[ -]?){12,19}\b", command):
            return "[REDACTED SENSITIVE COMMAND]"
        return command
