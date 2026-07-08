"""Pending confirmation handling for HI ROLEX."""

from __future__ import annotations

from assistant.command_models import TaskPlan


class ConfirmationManager:
    """Stores one pending plan that needs user confirmation."""

    def __init__(self) -> None:
        self.pending_plan: TaskPlan | None = None

    def set_pending_plan(self, plan: TaskPlan) -> None:
        """Store a plan awaiting confirmation."""
        self.pending_plan = plan

    def get_pending_plan(self) -> TaskPlan | None:
        """Return the current pending plan."""
        return self.pending_plan

    def clear_pending_plan(self) -> None:
        """Clear pending confirmation state."""
        self.pending_plan = None

    def has_pending_plan(self) -> bool:
        """Return True when a plan is waiting for confirmation."""
        return self.pending_plan is not None
