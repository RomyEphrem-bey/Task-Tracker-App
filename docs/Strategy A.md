# Task Tracker Architecture

## What it does

The Task Tracker combines a vanilla JavaScript board with a FastAPI API. Users can create, edit, filter, move, and delete tasks and manage nested comments. Tasks use `ToDo`, `InProgress`, and `Done` statuses. Data is stored in memory and is lost when the server restarts; there is no database or authentication.

## Data model

- `TaskCreate` defines new-task fields and defaults.
- `TaskUpdate` supports partial updates.
- `TaskResponse` adds an ID, comments, and timestamps.
- `CommentCreate` and `Comment` define comment input and output.
- Status values are `ToDo`, `InProgress`, and `Done`.
- Priority values are `Low`, `Medium`, and `High`.

Pydantic validates titles, tags, comments, enum values, and unexpected fields.

## Create-task flow

1. The frontend submits JSON to `POST /tasks`.
2. FastAPI and Pydantic validate the request.
3. `app/main.py` delegates creation to `storage.add_task`.
4. Storage generates a UUID and UTC timestamps and saves the task in `_tasks`.
5. The API returns `201 Created`.
6. The frontend reloads and renders the board.

## Key files

- `frontend/index.html`: UI, API calls, filtering, comments, and drag-and-drop.
- `app/main.py`: FastAPI setup and HTTP routes.
- `app/models.py`: API models and validation.
- `app/storage.py`: In-memory task and comment operations.
- `app/business_rules.py`: Status-transition rules.
- `tests/`: API behavior and storage-isolation tests.

## Conventions

Preserve API response shapes and exact status and priority values. Keep HTTP behavior in routes, storage operations in `storage.py`, and transition rules in `business_rules.py`. Use UUIDs, UTC timestamps, Pydantic v2, and pytest. Module 5 does not add authentication or a database.
