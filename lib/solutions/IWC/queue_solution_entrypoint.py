"""Public entrypoint exposing the typed queue implementation to the runner."""

from __future__ import annotations

from solutions.IWC.queue_solution_legacy import Queue
from solutions.IWC.task_types import TaskDispatch, TaskSubmission

class QueueSolutionEntrypoint:

    def __init__(self) -> None:
        self._queue: Queue = Queue()

    def enqueue(self, task: TaskSubmission) -> int:
        return self._queue.enqueue(task)

    def dequeue(self) -> TaskDispatch | None:
        return self._queue.dequeue()

    def size(self) -> int:
        return self._queue.size

    def age(self) -> int:
        return self._queue.age

    def purge(self) -> bool:
        return self._queue.purge()

