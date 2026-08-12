# Task Tracker Architecture - Strategy C

## Visible scope

The inspected API files implement task and nested-comment CRUD. Task lists support status, priority, and tag filters. Tasks are stored in an in-process dictionary, so data is not durable.

A frontend, health implementation, configuration details, tests, authentication, and deployment behavior were outside the targeted files reviewed for this strategy.

## Data model

- `TaskStatus`: `ToDo`, `InProgress`, or `Done`.
- `TaskPriority`: `Low`, `Medium`, or `High`.
- `TaskCreate`: validated new-task input.
- `TaskUpdate`: optional fields for partial updates.
- `TaskResponse`: task fields, ID, comments, and timestamps.
- `CommentCreate` and `Comment`: comment input and stored response.

Titles, tags, and comments are trimmed and validated. Request models forbid unexpected fields.

## Create-task flow

1. A client sends JSON to `POST /tasks`.
2. FastAPI binds and validates `TaskCreate`.
3. The route calls `storage.add_task`.
4. Storage generates a UUID and UTC timestamp and inserts the task into `_tasks`.
5. FastAPI returns the declared `TaskResponse` with `201 Created`.

Client behavior after the response was not visible in the targeted files.

## Key files

- `app/main.py`: API setup, routes, and HTTP errors.
- `app/models.py`: request and response models.
- `app/storage.py`: in-memory CRUD, filtering, IDs, and timestamps.

## Observed conventions

Partial updates use `model_dump(exclude_unset=True)`. Stored tasks are replaced with `model_copy(update=...)`. Missing tasks use `None`; comment deletion uses `False` to distinguish a missing comment. Status updates call an imported transition validator. `main.py` assigns `app` twice, with the second assignment becoming effective.
