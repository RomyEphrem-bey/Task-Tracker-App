from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskResponse, TaskStatus, TaskUpdate, Comment, CommentCreate


_tasks: dict[str, TaskResponse] = {}

#updated to include tags on add_task and update_task methods

def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task.

    Args:
        payload (TaskCreate): The task data to store.

    Returns:
        TaskResponse: The newly created task, with a generated `id`
            and `created_at`/`updated_at` timestamps set to the
            current time.
    """
    now = datetime.now(timezone.utc)

    task = TaskResponse(
    id=str(uuid4()),
    title=payload.title,
    description=payload.description if payload.description is not None else "",
    status=payload.status,
    priority=payload.priority,
    assignee=payload.assignee,
    tags=payload.tags,
    created_at=now,
    updated_at=now,
    )

    _tasks[task.id] = task

    return task

#updating this fct to support tags
def get_all_tasks(
    status: Optional["TaskStatus"] = None,
    priority: Optional["TaskPriority"] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """Return all stored tasks, optionally filtered.

    Args:
        status (Optional[TaskStatus]): If provided, only include tasks
            with this status.
        priority (Optional[TaskPriority]): If provided, only include
            tasks with this priority.
        tag (Optional[str]): If provided, only include tasks whose
            `tags` list contains this value (after stripping
            whitespace).

    Returns:
        list[TaskResponse]: The tasks matching all provided filters.
    """
    tasks = list(_tasks.values())

    if status is not None:
        tasks = [t for t in tasks if t.status == status]

    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]

    if tag is not None:
        cleaned_tag = tag.strip()
        tasks = [t for t in tasks if cleaned_tag in t.tags]

    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by its id.

    Args:
        task_id (str): The id of the task to look up.

    Returns:
        Optional[TaskResponse]: The matching task, or None if no task
            exists with that id.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): The fields to update. Only fields
            explicitly set on `payload` are applied; `updated_at` is
            always refreshed to the current time.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task
            exists with that id.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    updates["updated_at"] = datetime.now(timezone.utc)
    updated = task.model_copy(update=updates)
    _tasks[task_id] = updated
    return updated

def delete_task(task_id: str) -> bool:
    """Delete a stored task by its id.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        bool: True if the task existed and was deleted, False
            otherwise.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def add_comment(task_id: str, payload: CommentCreate) -> Optional[Comment]:
    """Add a comment to a stored task.

    Args:
        task_id (str): The id of the task to comment on.
        payload (CommentCreate): The comment data, containing `text`.

    Returns:
        Optional[Comment]: The newly created comment, or None if no
            task exists with that id.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    comment = Comment(
        id=str(uuid4()),
        text=payload.text,
        created_at=datetime.now(timezone.utc),
    )

    updated_task = task.model_copy(update={"comments": task.comments + [comment]})
    _tasks[task_id] = updated_task

    return comment


def get_comments_for_task(task_id: str) -> Optional[list[Comment]]:
    """Return all comments on a stored task.

    Args:
        task_id (str): The id of the task whose comments to retrieve.

    Returns:
        Optional[list[Comment]]: The task's comments, or None if no
            task exists with that id.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None
    return task.comments


def delete_comment(task_id: str, comment_id: str) -> Optional[bool]:
    """Delete a comment from a stored task.

    Args:
        task_id (str): The id of the task the comment belongs to.
        comment_id (str): The id of the comment to delete.

    Returns:
        Optional[bool]: None if no task exists with `task_id`; False
            if the task exists but no comment exists with
            `comment_id`; True if the comment was found and deleted.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    remaining_comments = [c for c in task.comments if c.id != comment_id]
    if len(remaining_comments) == len(task.comments):
        return False

    updated_task = task.model_copy(update={"comments": remaining_comments})
    _tasks[task_id] = updated_task
    return True


def _reset() -> None:
    _tasks.clear()