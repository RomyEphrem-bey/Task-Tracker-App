# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project layout

The actual application lives entirely under `task-tracker-api/`. All commands below assume that directory as the working directory.

- `task-tracker-api/app/` — FastAPI backend
- `task-tracker-api/frontend/index.html` — single-file vanilla HTML/CSS/JS frontend (no build step)
- `task-tracker-api/tests/` — pytest test suite
- `task-tracker-api/docs/midcourse/` — mini-ADRs, user stories, and manual verification notes for features added mid-course (read these before adding a new feature — they record which architecture alternatives were already considered and rejected, and why)

## Commands

Run from `task-tracker-api/`:

**Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Environment setup:** Copy `.env.example` to `.env` (Windows: `Copy-Item .env.example .env`). Variables: `PORT` (default `8000`), `APP_ENV` (default `development`).

**Run the dev server:**
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive docs are at `http://localhost:8000/docs` when the server is running.

**Run all tests:**
```bash
pytest
```

**Run a single test:**
```bash
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body
```

There is no lint/build step configured for this project.

## Architecture

The API is a single FastAPI app with **in-memory storage** — no database. All task data lives in a module-level dict (`app/storage.py::_tasks`) and is lost on restart. `storage._reset()` clears this dict and is called by the `_reset_storage` autouse fixture in `tests/conftest.py` before/after every test.

**Request flow:**
```
HTTP request → app/main.py (route handlers) → app/storage.py (CRUD) → TaskResponse
                            ↓
                 app/business_rules.py (status transition validation, called from PATCH handler)
```

**Key layers:**
- `app/main.py` — FastAPI instance, CORS middleware, and all task + comment route handlers (`/tasks` CRUD, `/tasks/{id}/comments`). New routers are registered here via `app.include_router(...)`.
- `app/models.py` — Pydantic models: `TaskCreate` (input), `TaskUpdate` (partial input), `TaskResponse` (output), `Comment`/`CommentCreate`, and `HealthResponse`. Enums `TaskStatus` (`ToDo`/`InProgress`/`Done`) and `TaskPriority` (`Low`/`Medium`/`High`) live here.
- `app/storage.py` — Pure functions operating on the in-memory `_tasks` dict. All filtering (by status/priority) and comment CRUD happen here. (`app/storage/` — the directory — holds only `.gitkeep` and is unused; don't confuse it with this module.)
- `app/business_rules.py` — Status transition whitelist (`VALID_TRANSITIONS`). Only allowed forward progression is `ToDo → InProgress → Done`; `Done` can go back to `InProgress`. Direct `ToDo → Done` and backward `InProgress → ToDo` are rejected with 422.
- `app/core/config.py` — `Settings` object (pydantic-settings) loaded from `.env`. Imported as `settings` singleton.
- `app/api/routes/health.py` — `GET /health` endpoint, its own `APIRouter`, mounted via `include_router` — a template for future route modules.
- `app/models/health.py` — dead code. `app/models/` has no `__init__.py`, so `app/models.py` (the file) shadows it; `HealthResponse` actually resolves from `app/models.py`, not here.

**Tags and comments are embedded on the task, not separate collections** (see `docs/midcourse/mini-adr.md` for the alternatives considered and why):
- Tags: `tags: list[str]` on `TaskCreate`/`TaskUpdate`/`TaskResponse`, validated/deduped by `validate_tags()` in `app/models.py`. Matching is case-sensitive (`"Backend"` ≠ `"backend"`) — documented, not a bug.
- Comments: `comments: list[Comment]` on `TaskResponse` only (not on create/update). Managed via nested routes `/tasks/{task_id}/comments[/{comment_id}]` in `main.py`, backed by helpers in `storage.py`.

**Partial updates rely on Pydantic's `exclude_unset`.** `storage.update_task()` calls `payload.model_dump(exclude_unset=True)`, so an omitted field on `TaskUpdate` leaves the existing value untouched, while an explicit empty value (e.g. `tags: []`) clears it.

**Testing:** `tests/conftest.py`'s autouse fixture resets storage between tests; the `client` fixture wraps the app in FastAPI's `TestClient`. Tests are split across `tests/test_tasks.py` and `tests/test_comments.py`.

**Adding new routes:** Tasks and comments are defined directly as `@app.<method>` handlers in `app/main.py` rather than per-feature route modules — follow that pattern unless doing a deliberate refactor. `app/api/routes/health.py` is the one exception, kept as a template for a future move to per-feature modules.

**CORS** in `main.py` hardcodes allowed origins for local frontend dev servers (`localhost:5500`, `localhost:5173`, and `null` for `file://` pages) — update this list if the frontend is served from a different origin.

**Frontend** (`frontend/index.html`) is a single static file, no build step. Hits the API at hardcoded `API_BASE = "http://localhost:8000"`, implements a drag-and-drop Kanban board (ToDo/InProgress/Done) where dragging a card issues a `PATCH` to update status, with optimistic UI update and rollback on failure.
