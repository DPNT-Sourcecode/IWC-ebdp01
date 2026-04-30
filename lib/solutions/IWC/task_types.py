"""Typed helpers shared across queue implementations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TaskSubmission:
    """Typed payload accepted by ``Queue.enqueue``."""

    provider: str
    user_id: int
    timestamp: datetime | str
    metadata: dict[str, object] = field(default_factory=dict)

@dataclass
class TaskDispatch:
    """Typed payload returned by ``Queue.dequeue``."""

    provider: str
    user_id: int


__all__ = ["TaskSubmission", "TaskDispatch"]
