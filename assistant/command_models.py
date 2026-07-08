"""Structured command models for HI ROLEX."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CommandIntent:
    """Classified intent for one user command step."""

    category: str
    raw_text: str
    target: str = ""
    destination: str = ""
    parameters: dict[str, str] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass(frozen=True)
class PlannedAction:
    """Executable action planned from a command intent."""

    action_id: int
    intent: CommandIntent
    description: str
    requires_confirmation: bool = False


@dataclass(frozen=True)
class TaskPlan:
    """Ordered action plan for a user command."""

    original_text: str
    actions: list[PlannedAction]

    @property
    def requires_confirmation(self) -> bool:
        """Return True when any planned action needs confirmation."""
        return any(action.requires_confirmation for action in self.actions)


@dataclass(frozen=True)
class CommandResult:
    """Result returned to GUI and voice systems."""

    success: bool
    message: str
    action_details: str = ""
    confirmation_required: bool = False
    pending_action: PlannedAction | None = None
    pending_plan: TaskPlan | None = None
