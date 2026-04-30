from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

# LEGACY CODE ASSET
# RESOLVED on deploy
from solutions.IWC.task_types import TaskSubmission, TaskDispatch

class Priority(IntEnum):
    """Represents the queue ordering tiers observed in the legacy system."""
    HIGH = 1
    NORMAL = 2

@dataclass
class Provider:
    name: str
    base_url: str
    depends_on: list[str]

MAX_TIMESTAMP = datetime.max.replace(tzinfo=None)

COMPANIES_HOUSE_PROVIDER = Provider(
    name="companies_house", base_url="https://fake.companieshouse.co.uk", depends_on=[]
)


CREDIT_CHECK_PROVIDER = Provider(
    name="credit_check",
    base_url="https://fake.creditcheck.co.uk",
    depends_on=["companies_house"],
)


BANK_STATEMENTS_PROVIDER = Provider(
    name="bank_statements", base_url="https://fake.bankstatements.co.uk", depends_on=[]
)

ID_VERIFICATION_PROVIDER = Provider(
    name="id_verification", base_url="https://fake.idv.co.uk", depends_on=[]
)


REGISTERED_PROVIDERS: list[Provider] = [
    BANK_STATEMENTS_PROVIDER,
    COMPANIES_HOUSE_PROVIDER,
    CREDIT_CHECK_PROVIDER,
    ID_VERIFICATION_PROVIDER,
]

class Queue:
    def __init__(self):
        self._queue = []
        self._task_map = {}

    def _collect_dependencies(self, task: TaskSubmission) -> list[TaskSubmission]:
        provider = next((p for p in REGISTERED_PROVIDERS if p.name == task.provider), None)
        if provider is None:
            return []

        tasks: list[TaskSubmission] = []
        for dependency in provider.depends_on:
            dependency_task = TaskSubmission(
                provider=dependency,
                user_id=task.user_id,
                timestamp=task.timestamp,
            )
            tasks.extend(self._collect_dependencies(dependency_task))
            tasks.append(dependency_task)
        return tasks

    @staticmethod
    def _priority_for_task(task):
        metadata = task.metadata
        raw_priority = metadata.get("priority", Priority.NORMAL)
        try:
            return Priority(raw_priority)
        except (TypeError, ValueError):
            return Priority.NORMAL

    @staticmethod
    def _earliest_group_timestamp_for_task(task):
        metadata = task.metadata
        return metadata.get("group_earliest_timestamp", MAX_TIMESTAMP)

    @staticmethod
    def _timestamp_for_task(task):
        timestamp = task.timestamp
        if isinstance(timestamp, datetime):
            return timestamp.replace(tzinfo=None)
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp).replace(tzinfo=None)
        return timestamp


    def enqueue(self, item: TaskSubmission) -> int:
        tasks = [*self._collect_dependencies(item), item]

        for task in tasks:
            key = (task.user_id, task.provider)
            existing_task = self._task_map.get(key)

            if existing_task is not None:
                if self._timestamp_for_task(task) < self._timestamp_for_task(existing_task):
                    existing_task.timestamp = task.timestamp
                continue

            metadata = task.metadata
            metadata.setdefault("priority", Priority.NORMAL)
            metadata.setdefault("group_earliest_timestamp", MAX_TIMESTAMP)
            self._queue.append(task)
            self._task_map[key] = task
        return self.size
    
    def dequeue(self):
        """Return the next task using R1-R5 queue ordering rules."""
        if self.size == 0:
            return None

        fifo_positions = {id(task): idx for idx, task in enumerate(self._queue)}

        user_ids = {task.user_id for task in self._queue}
        task_count = {}
        priority_timestamps = {}

        for user_id in user_ids:
            user_tasks = [t for t in self._queue if t.user_id == user_id]
            earliest_task = min(
                user_tasks,
                key=lambda t: (self._timestamp_for_task(t), fifo_positions[id(t)]),
            )
            priority_timestamps[user_id] = earliest_task.timestamp
            task_count[user_id] = len(user_tasks)

        for task in self._queue:
            metadata = task.metadata
            raw_priority = metadata.get("priority")

            try:
                priority_level = Priority(raw_priority)
            except (TypeError, ValueError):
                priority_level = None

            if priority_level is None or priority_level == Priority.NORMAL:
                metadata["group_earliest_timestamp"] = MAX_TIMESTAMP

                if task_count[task.user_id] >= 3:
                    metadata["group_earliest_timestamp"] = priority_timestamps[task.user_id]
                    metadata["priority"] = Priority.HIGH
                else:
                    metadata["priority"] = Priority.NORMAL
            else:
                metadata["group_earliest_timestamp"] = metadata.get(
                    "group_earliest_timestamp", MAX_TIMESTAMP
                )

        newest_ts = max(self._timestamp_for_task(task) for task in self._queue)

        def is_old_bank(task):
            """Bank statements becomes time-sensitive after 5 minutes in queue age."""
            if task.provider != "bank_statements":
                return False
            age_seconds = (
                newest_ts - self._timestamp_for_task(task)
            ).total_seconds()
            return age_seconds >= 300

        has_old_bank = any(is_old_bank(task) for task in self._queue)

        if has_old_bank:

            self._queue.sort(
                key=lambda task: (
                    self._timestamp_for_task(task),
                    0 if is_old_bank(task) else 1,
                    fifo_positions[id(task)],
                )
            )
        else:
            self._queue.sort(
                key=lambda task: (
                    self._priority_for_task(task).value,
                    self._earliest_group_timestamp_for_task(task),
                    task.provider == "bank_statements",
                    self._timestamp_for_task(task),
                    fifo_positions[id(task)],
                )
            )

        task = self._queue.pop(0)
        self._task_map.pop((task.user_id, task.provider), None)

        return TaskDispatch(
            provider=task.provider,
            user_id=task.user_id,
        )

    @property
    def age(self):
        if not self._queue:
            return 0
        timestamps = [self._timestamp_for_task(task) for task in self._queue]
        return int((max(timestamps) - min(timestamps)).total_seconds())
    
    @property
    def size(self):
        return len(self._queue)

    def purge(self):
        self._queue.clear()
        self._task_map.clear()
        return True

"""
===================================================================================================

The following code is only to visualise the final usecase.
No changes are needed past this point.

To test the correct behaviour of the queue system, import the `Queue` class directly in your tests.

===================================================================================================

```python
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(queue_worker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Queue worker cancelled on shutdown.")


app = FastAPI(lifespan=lifespan)
queue = Queue()


@app.get("/")
def read_root():
    return {
        "registered_providers": [
            {"name": p.name, "base_url": p.base_url} for p in registered_providers
        ]
    }


class DataRequest(BaseModel):
    user_id: int
    providers: list[str]


@app.post("/fetch_customer_data")
def fetch_customer_data(data: DataRequest):
    provider_names = [p.name for p in registered_providers]

    for provider in data.providers:
        if provider not in provider_names:
            logger.warning(f"Provider {provider} doesn't exists. Skipping")
            continue

        queue.enqueue(
            TaskSubmission(
                provider=provider,
                user_id=data.user_id,
                timestamp=datetime.now(),
            )
        )

    return {"status": f"{len(data.providers)} Task(s) added to queue"}


async def queue_worker():
    while True:
        if queue.size == 0:
            await asyncio.sleep(1)
            continue

        task = queue.dequeue()
        if not task:
            continue

        logger.info(f"Processing task: {task}")
        await asyncio.sleep(2)
        logger.info(f"Finished task: {task}")
```
"""

