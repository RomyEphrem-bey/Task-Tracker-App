# Task Tracker Architecture

## Scope

This document describes the current implementation of the Task Tracker App,
not a proposed future architecture. Paths below are relative to
`task-tracker-api/` unless stated otherwise.

## System overview

The application has three layers:

### Frontend

`frontend/index.html` is a single-file vanilla JavaScript board. It owns
presentation, temporary client state, tag filtering, forms, API calls,
comments, and drag-and-drop. It calls the API at `http://localhost:8000`.

### API and validation

FastAPI handles the HTTP boundary, CORS, request parsing, response
serialization, and error mapping. Pydantic models validate API contracts.
Task and comment routes are in `app/main.py`; `GET /health` uses a separate
router.

### Storage and business rules

`app/storage.py` stores tasks and nested comments in a process-local
dictionary and generates UUIDs and UTC timestamps. `app/business_rules.py`
validates status changes. There is no database or authentication, and all
data is lost when the API process restarts.

## Data model

- Tasks contain a title, description, status, priority, assignee, tags,
  comments, ID, and timestamps.
- Comments contain text, an ID, and a creation timestamp.
- Status values are `ToDo`, `InProgress`, and `Done`.
- Priority values are `Low`, `Medium`, and `High`.

`TaskCreate` defines creation input, `TaskUpdate` supports partial updates,
and `TaskResponse` defines API output. Pydantic trims and validates titles,
tags, and comment text and rejects unexpected request fields.

## Request flow

1. The frontend sends JSON to `POST /tasks`.
2. FastAPI binds the body to `TaskCreate`, and Pydantic validates it.
3. `app/main.py` delegates creation to `storage.add_task`.
4. Storage generates a UUID and UTC timestamps and inserts the task into
   `_tasks`.
5. FastAPI returns `TaskResponse` with `201 Created`, and the frontend reloads
   the board.

## Rules and constraints

- Preserve existing API response shapes and exact status and priority values.
- Valid moves include self-transitions, `ToDo -> InProgress`,
  `InProgress -> Done`, and `Done -> InProgress`; other moves return `422`.
- Creation returns `201`, deletion returns an empty `204`, missing resources
  return `404`, and invalid input or transitions return `422`.
- Keep HTTP behavior in routes, schemas in `models.py`, storage operations in
  `storage.py`, and transition rules in `business_rules.py`.
- Module 5 does not add authentication, a database, or dependencies.
- Run the API with `uvicorn app.main:app --reload` and tests with `pytest -v`.

## Key files

| File | Responsibility |
|---|---|
| `frontend/index.html` | Browser UI and API client. |
| `app/main.py` | FastAPI application and task/comment routes. |
| `app/models.py` | Active Pydantic schemas and validation. |
| `app/storage.py` | In-memory task and comment operations. |
| `app/business_rules.py` | Status-transition policy. |
| `app/api/routes/health.py` | Health endpoint. |

Tests under `tests/` verify API behavior and reset storage between tests.

## Current limitations and known issues

- `app/main.py` assigns `app` twice. The second `FastAPI(...)` instance
  replaces the first and becomes the effective application.
- `app/models/health.py` duplicates the active `HealthResponse` in
  `app/models.py`.
- `AGENTS.md` specifies Python 3.11, while the README states Python 3.12+.
  This is a documentation mismatch that should be resolved.

## Context Strategy Comparison

### Strategy A - Minimal Context

What it got right: TODO
What it got wrong or invented: TODO

### Strategy B - Structured Context

What it got right: TODO
What it got wrong or missed: TODO

### Strategy C - Targeted Context

What it got right: TODO
What it got wrong or missed: TODO

### Verdict

I picked Strategy TODO because TODO.

### My context rule

For TODO task shape, I use TODO strategy because TODO.
For TODO task shape, I use TODO strategy because TODO.
