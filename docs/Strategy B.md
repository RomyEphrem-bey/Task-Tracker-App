# Task Tracker Architecture - Strategy B

## System overview

The application has three main layers:

1. A single-file vanilla JavaScript frontend.
2. A FastAPI HTTP and validation layer.
3. An in-memory storage layer.

Users manage tasks, tags, comments, and status changes. The backend also exposes `GET /health`. Data is process-local and temporary.

## Responsibilities

- `frontend/index.html`: presentation, client state, filtering, API calls, comments, and drag-and-drop.
- `app/main.py`: effective FastAPI app, CORS, routes, response models, and HTTP errors.
- `app/models.py`: active Pydantic schemas, enums, defaults, and validation.
- `app/storage.py`: task/comment CRUD, filtering, UUIDs, and timestamps.
- `app/business_rules.py`: allowed status transitions.
- `app/core/config.py`: environment-backed settings.
- `app/api/routes/health.py`: health endpoint.
- `tests/`: API verification and storage reset between tests.

## Create-task flow

The frontend sends `POST /tasks`. Pydantic validates `TaskCreate`, `main.py` delegates to storage, and storage creates a `TaskResponse` with a UUID and UTC timestamps. FastAPI returns `201`, and the frontend reloads the task list.

## Rules and conventions

Status values are `ToDo`, `InProgress`, and `Done`; priority values are `Low`, `Medium`, and `High`. Valid moves include self-transitions, `ToDo -> InProgress`, `InProgress -> Done`, and `Done -> InProgress`. Missing resources return `404`, invalid input or transitions return `422`, creation returns `201`, and deletion returns `204`.

## Visible inconsistencies

- `main.py` creates two FastAPI instances; the second is the effective app.
- `app/models/health.py` duplicates the active health schema in `app/models.py`.
- `AGENTS.md` specifies Python 3.11, while the README specifies Python 3.12+.
