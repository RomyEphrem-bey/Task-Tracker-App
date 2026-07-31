from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskResponse, TaskUpdate


_tasks: dict[str, TaskResponse] = {}

def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)

    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description if payload.description is not None else "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        created_at=now,
        updated_at=now,
    )

    _tasks[task.id] = task

    return task

def get_all_tasks(
    status: Optional["TaskStatus"] = None,
    priority: Optional["TaskPriority"] = None,
) -> list[TaskResponse]:
    tasks = list[TaskResponse](_tasks.values())

    if status is not None:
        tasks = [t for t in tasks if t.status == status]

    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]

    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    updates["updated_at"] = datetime.now(timezone.utc)
    updated = task.model_copy(update=updates)
    _tasks[task_id] = updated
    return updated

def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()