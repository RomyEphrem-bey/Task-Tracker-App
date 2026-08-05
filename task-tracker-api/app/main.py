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
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
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
    print(f"[startup] APP_ENV={settings.app_env} PORT={settings.port}")