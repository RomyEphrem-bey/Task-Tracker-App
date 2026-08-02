# Mini-ADR: Mid-Course Feature Additions

Status: Feature 1 (Tags) implemented. Feature 2 (Task Comments) — plan decided below, implementation not yet started.

## Feature 1: Tags / Labels

### Context
The existing Task Tracker uses FastAPI, Pydantic, in-memory storage, and a vanilla HTML/CSS/JavaScript frontend. The requested addition was optional task tags: tag creation on task creation, tag editing, validation, display, and filtering — without changing any unrelated existing behavior.

### Alternatives AI suggested
Two lightweight architectures were requested and compared:

- **Architecture A — Tags embedded directly on each task.** Tags stored as `list[str]` directly on the `Task` model. No new entities, endpoints, or storage structures.
- **Architecture B — Separate tag catalogue with task-to-tag associations.** A central `_tags` dictionary keyed by tag ID, plus a normalized name index, with tasks holding `tag_ids` instead of tag strings directly.

### Decision
**Architecture A.** Tags are stored as a list of trimmed strings directly on each task (`app/models.py`, `app/storage.py`).

### Rejected as too complex / out of scope
Architecture B was rejected. It would have added a canonical tag catalogue, ID-to-name resolution on every response, and cleanup logic to keep task/tag associations consistent — none of which was needed by the five user stories, and all of which would have introduced more failure paths (association bugs, orphaned tags, index drift) for no requested benefit. It's only justified if tags were expected to become managed entities with colors, descriptions, or centralized administration, which was never asked for.

### What was implemented
- `app/models.py` — `tags: list[str]` added to `TaskCreate`, `TaskUpdate`, `TaskResponse`; a shared `validate_tags()` validator trims whitespace, rejects blank-after-trim tags with 422, and removes exact-string duplicates.
- `app/storage.py` — `add_task()` stores tags as-is (already validated); `get_all_tasks()` accepts an optional `tag` filter using exact substring-in-list matching; `update_task()` relies on Pydantic's `exclude_unset=True` so omitted `tags` leave existing tags untouched, while `tags: []` clears them.
- `app/main.py` — `GET /tasks` gained an optional `tag` query parameter, no new endpoint.
- `frontend/index.html` — tag input in the create/edit modal, tag chips on cards, a tag filter with Apply/Clear controls above the board.

### Known limitation (see verification.md for break test)
Tag matching (both dedup on create and the `?tag=` filter) is **case-sensitive**. `"Backend"` and `"backend"` are treated as different tags. This was identified during manual testing but not yet formally broken/documented as a test — see `verification.md`.

## Feature 2: Task Comments

### Context
Each task should support a small discussion thread: add a comment, list all comments for a task, and delete one. Text must be non-blank after trimming, and both operations must return 404 correctly when the task (or comment) doesn't exist.

### Alternatives AI suggested

**Architecture A — Comments embedded as a list on each task.** Add a `Comment` model (`id`, `text`, `created_at`) and store `comments: list[Comment] = []` directly on the `Task`. No separate storage; comment count is just `len(task.comments)`.

**Architecture B — Separate comments store.** A top-level `_comments: dict[comment_id, Comment]`, where each `Comment` holds its own `task_id`. Comments are decoupled from the `Task` object itself and looked up by filtering on `task_id`.

| | Architecture A (embedded list) | Architecture B (separate store) |
|---|---|---|
| Storage | `comments` field on `Task` | New `_comments` dict, keyed by `comment_id` |
| Matches existing Tags pattern | Yes — same embed-on-task style | No — introduces a second top-level collection |
| Task delete cleanup | Automatic (comments live inside the task) | Manual — must remove orphaned comments in `delete_task()` |
| Comment count for card display | Trivial: `len(task.comments)` | Requires a filter/count over `_comments` per task |
| Future flexibility (e.g. comments independent of a task lifecycle) | Low | Higher — comments are independent records |
| Code required | Smaller | Slightly larger (new store, index, cleanup path) |

### Decision
**Architecture B.** Comments are stored in a separate `_comments` dict, keyed by comment ID, with each comment record holding the `task_id` it belongs to.

### Rejected as too complex / out of scope
Architecture A was not chosen for this feature, despite being the smaller change and the same pattern used for Tags — Architecture B was deliberately picked to keep comment storage decoupled from the task record itself.

### Route design note
Architecture B's natural delete route would be flat (`DELETE /comments/{comment_id}`), but that can't return 404 for "task not found" (Story 3's requirement) and would be the only non-`/tasks/{task_id}/...`-nested route in the API. Decision: keep the storage separate (Architecture B) but nest the route as `DELETE /tasks/{task_id}/comments/{comment_id}`, so it validates the task exists and stays consistent with `POST/GET /tasks/{task_id}/comments`.

### Planned endpoints
- `POST /tasks/{task_id}/comments` — add a comment; 404 if task missing, 422 if text is blank after trimming.
- `GET /tasks/{task_id}/comments` — list comments for a task in insertion order; 404 if task missing; empty list if task has none.
- `DELETE /tasks/{task_id}/comments/{comment_id}` — delete one comment; 404 if task missing or comment missing/not belonging to that task.

### Planned data model
```
Comment
 ├─ id: string
 ├─ task_id: string
 ├─ text: string
 └─ created_at: datetime
```

### Files expected to change
- `app/models.py` — new `Comment`/`CommentCreate` models, text validator (trim, reject blank).
- `app/storage.py` — new `_comments` dict, `add_comment()`, `get_comments_for_task()`, `delete_comment()`, and cleanup of a task's comments inside `delete_task()`.
- `app/main.py` — three new nested routes listed above.
- `frontend/index.html` — comment list/add/delete UI in the task edit view, comment count on cards.
- `tests/test_tasks.py` (or a new `tests/test_comments.py`) — coverage per Story 1-3 and 5.

_Implementation not yet started 