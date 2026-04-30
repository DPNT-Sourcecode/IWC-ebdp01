from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Iterable

from solutions.IWC.queue_solution_entrypoint import QueueSolutionEntrypoint
from solutions.IWC.task_types import TaskDispatch, TaskSubmission


DEFAULT_SCENARIO_BASE = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)


def iso_ts(*, base: datetime = DEFAULT_SCENARIO_BASE, delta_minutes: int = 0) -> str:
    return str(base + timedelta(minutes=delta_minutes))


class QueueActionBuilder:
    def __init__(
        self,
        name: str,
        payload: Any | None = None,
        expect_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._name = name
        self._payload = payload
        self._expect_factory = expect_factory or (lambda value: value)

    def expect(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        expectation = self._expect_factory(*args, **kwargs)
        return {"name": self._name, "input": self._payload, "expect": expectation}


def call_enqueue(provider: str, user_id: int, timestamp: str) -> QueueActionBuilder:
    return QueueActionBuilder(
        "enqueue",
        TaskSubmission(provider=provider, user_id=user_id, timestamp=timestamp),
    )


def call_size() -> QueueActionBuilder:
    return QueueActionBuilder("size")


def call_dequeue() -> QueueActionBuilder:
    return QueueActionBuilder(
        "dequeue",
        expect_factory=lambda provider, user_id: TaskDispatch(
            provider=provider, user_id=user_id
        ),
    )


def run_queue(actions: Iterable[dict[str, Any]]) -> None:
    queue = QueueSolutionEntrypoint()
    for position, step in enumerate(actions, start=1):
        method: Callable[..., Any] = getattr(queue, step["name"])
        args = () if step["input"] is None else (step["input"],)
        actual = method(*args)
        expected = step["expect"]
        if actual != expected:
            payload = step.get("input")
            payload_repr = "" if payload is None else f" input={payload!r}"
            raise AssertionError(
                "Step {} '{}'{} expected {!r} but got {!r}".format(
                    position,
                    step["name"],
                    payload_repr,
                    expected,
                    actual,
                )
            )


__all__ = ["iso_ts", "call_enqueue", "call_size", "call_dequeue", "run_queue"]
