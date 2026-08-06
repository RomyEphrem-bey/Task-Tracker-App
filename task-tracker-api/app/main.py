# main.py — Application entry point.
# Creates the FastAPI instance, loads config, and registers all routers.
# Run with: uvicorn app.main:app --reload

#from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, status, Response
from typing import Optional
from app import storage
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority, Comment, CommentCreate
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.business_rules import validate_status_transition

from fastapi.middleware.cors import CORSMiddleware

# Create the FastAPI application instance.
# The title and version appear in the auto-generated /docs (Swagger UI).
app = FastAPI(
    title="Task Tracker API",
    version="0.1.0",
    description="A learning-focused REST API built with FastAPI and JSON file storage",
)

app = FastAPI(
    title="Task Tracker API",
    description="...",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers.
# All routes defined in health_router are mounted at the root path.
# Add future routers here (e.g., tasks, projects) as the app grows.
app.include_router(health_router)

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED, tags=["tasks"]
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload (TaskCreate): The task data to create, including title,
            description, status, priority, assignee, and tags.

    Returns:
        TaskResponse: The newly created task, including its generated
            `id`, `created_at`, and `updated_at` timestamps.

    Example:
        POST /tasks
        {"title": "Write docs", "priority": "High"}
        -> 201 Created
        {
            "id": "...",
            "title": "Write docs",
            "description": "",
            "status": "ToDo",
            "priority": "High",
            "assignee": null,
            "tags": [],
            "comments": [],
            "created_at": "...",
            "updated_at": "..."
        }
    """
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, and/or tag.

    Args:
        status (Optional[TaskStatus]): If provided, only return tasks
            with this status.
        priority (Optional[TaskPriority]): If provided, only return
            tasks with this priority.
        tag (Optional[str]): If provided, only return tasks whose
            `tags` list contains this value (after stripping
            whitespace).

    Returns:
        list[TaskResponse]: The tasks matching all provided filters.

    Example:
        GET /tasks?status=ToDo&priority=High
        -> 200 OK
        [{"id": "...", "title": "...", "status": "ToDo", "priority": "High", ...}]
    """
    return storage.get_all_tasks(
        status=status,
        priority=priority,
        tag=tag,
    )

@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def get_task_by_id(task_id: str) -> TaskResponse:
    """Retrieve a single task by its id.

    Args:
        task_id (str): The id of the task to retrieve.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 Not Found if no task exists with `task_id`.

    Example:
        GET /tasks/{task_id}
        -> 200 OK
        {"id": "...", "title": "...", ...}
    """
    task = storage.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

#@app.patch(
#    "/tasks/{task_id}",
#    response_model=TaskResponse,
#    tags=["tasks"],
#)
#def update_task_route(
#    task_id: str,
#    payload: TaskUpdate,
#) -> TaskResponse:
#    updated = storage.update_task(task_id, payload)

#    if updated is None:
#        raise HTTPException(
#            status_code=404,
#            detail=f"Task with id '{task_id}' not found",
#        )

#    return updated

@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task_route(
    task_id: str,
    payload: TaskUpdate,
) -> TaskResponse:
    """Apply a partial update to an existing task.

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): The fields to update. Fields left unset
            are not modified; if `status` is provided, it is validated
            against the allowed status transitions before being
            applied.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 Not Found if no task exists with `task_id`.
        HTTPException: 422 Unprocessable Entity if `payload.status` is
            not a valid transition from the task's current status
            (raised by `validate_status_transition`).

    Example:
        PATCH /tasks/{task_id}
        {"status": "InProgress"}
        -> 200 OK
        {"id": "...", "status": "InProgress", ...}
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id '{task_id}' not found",
            )

        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found",
        )

    return updated

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str) -> Response:
    """Delete a task by its id.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        Response: An empty response with status code 204 No Content.

    Raises:
        HTTPException: 404 Not Found if no task exists with `task_id`.

    Example:
        DELETE /tasks/{task_id}
        -> 204 No Content
    """
    deleted = storage.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post(
    "/tasks/{task_id}/comments",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
    tags=["comments"],
)
def add_comment(task_id: str, payload: CommentCreate) -> Comment:
    """Add a comment to a task.

    Args:
        task_id (str): The id of the task to comment on.
        payload (CommentCreate): The comment data, containing `text`.

    Returns:
        Comment: The newly created comment, including its generated
            `id` and `created_at` timestamp.

    Raises:
        HTTPException: 404 Not Found if no task exists with `task_id`.

    Example:
        POST /tasks/{task_id}/comments
        {"text": "Looks good"}
        -> 201 Created
        {"id": "...", "text": "Looks good", "created_at": "..."}
    """
    comment = storage.add_comment(task_id, payload)

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found",
        )

    return comment


@app.get(
    "/tasks/{task_id}/comments",
    response_model=list[Comment],
    tags=["comments"],
)
def list_comments(task_id: str) -> list[Comment]:
    """List all comments on a task.

    Args:
        task_id (str): The id of the task whose comments to list.

    Returns:
        list[Comment]: The task's comments.

    Raises:
        HTTPException: 404 Not Found if no task exists with `task_id`.

    Example:
        GET /tasks/{task_id}/comments
        -> 200 OK
        [{"id": "...", "text": "...", "created_at": "..."}]
    """
    comments = storage.get_comments_for_task(task_id)

    if comments is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found",
        )

    return comments


@app.delete(
    "/tasks/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["comments"],
)
def delete_comment(task_id: str, comment_id: str) -> Response:
    """Delete a comment from a task.

    Args:
        task_id (str): The id of the task the comment belongs to.
        comment_id (str): The id of the comment to delete.

    Returns:
        Response: An empty response with status code 204 No Content.

    Raises:
        HTTPException: 404 Not Found if no task exists with `task_id`.
        HTTPException: 404 Not Found if no comment exists with
            `comment_id` on that task.

    Example:
        DELETE /tasks/{task_id}/comments/{comment_id}
        -> 204 No Content
    """
    result = storage.delete_comment(task_id, comment_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found",
        )

    if result is False:
        raise HTTPException(
            status_code=404,
            detail=f"Comment with id '{comment_id}' not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Optional: log the active environment on startup so it's clear which
# .env values were loaded (helpful when switching between dev/prod configs).
@app.on_event("startup")
async def on_startup() -> None:
    """Log the active environment and port when the application starts.

    Returns:
        None
    """
    print(f"[startup] APP_ENV={settings.app_env} PORT={settings.port}")