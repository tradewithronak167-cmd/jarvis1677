"""Rule-based task planner for HI ROLEX."""

from __future__ import annotations

import re

from assistant.command_models import PlannedAction, TaskPlan
from assistant.intent_classifier import IntentClassifier


class TaskPlanner:
    """Creates ordered plans from simple single or multi-step commands."""

    def __init__(self, intent_classifier: IntentClassifier | None = None) -> None:
        self.intent_classifier = intent_classifier or IntentClassifier()

    def create_plan(self, text: str) -> TaskPlan:
        """Create a task plan from user text."""
        steps = self._split_steps(text)
        actions: list[PlannedAction] = []
        for index, step in enumerate(steps, start=1):
            intent = self.intent_classifier.classify(step)
            actions.append(
                PlannedAction(
                    action_id=index,
                    intent=intent,
                    description=self._describe_intent(intent),
                    requires_confirmation=intent.requires_confirmation,
                )
            )
        return TaskPlan(original_text=text, actions=actions)

    def _split_steps(self, text: str) -> list[str]:
        """Split predictable multi-step commands into ordered steps."""
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            return []

        # Avoid splitting search queries that naturally contain "and".
        if cleaned.casefold().startswith("search google for "):
            return [cleaned]

        parts = re.split(r"\s+(?:and then|after that|then)\s+|,\s*", cleaned, flags=re.I)
        if len(parts) == 1:
            parts = re.split(r"\s+and\s+", cleaned, flags=re.I)
        return [part.strip() for part in parts if part.strip()]

    def _describe_intent(self, intent: object) -> str:
        """Return user-friendly action text."""
        category = intent.category
        if category == "open_app":
            return f"Open {intent.target}"
        if category == "close_app":
            return f"Close {intent.target}"
        if category == "open_website":
            return f"Open website {intent.target}"
        if category == "google_search":
            return f"Search Google for {intent.target}"
        if category == "open_folder":
            return f"Open folder {intent.target}"
        if category == "hardware_status":
            return f"Check {intent.target} status"
        if category == "hardware_control":
            return f"Set {intent.target} to {intent.destination}%"
        if category == "memory_store":
            return "Save a memory"
        if category == "memory_query":
            return "Read saved memories"
        if category == "memory_delete":
            return f"Delete memory: {intent.target}"
        if category == "file_operation":
            operation = intent.parameters.get("operation", "file operation")
            return f"{operation.replace('_', ' ').title()} {intent.target}"
        if category == "ai_chat":
            return "Ask AI"
        return "Unsupported or unknown request"
