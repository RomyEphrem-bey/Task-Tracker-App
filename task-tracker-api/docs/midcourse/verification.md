# Verification — Feature 1: Tags / Labels

## 1. Baseline check
Before/independent of the Tags changes, the app starts and responds correctly:
- `GET /health` → `200 {"status": "ok", "timestamp": "..."}`
- Full pytest suite (14 pre-existing tests covering create/list/patch/delete/status-transition validation) passes independently of the tag tests.

## 2. Backend test results
Full suite run: `python -m pytest tests/ -v`

```
23 passed, 3 warnings in 0.59s
```

14 pre-existing tests (task CRUD, validation, status transitions) + 9 new Tags tests:
- `test_create_task_with_tags`
- `test_create_task_without_tags`
- `test_create_task_trims_tags`
- `test_create_task_rejects_blank_tag`
- `test_update_only_tags_preserves_other_fields`
- `test_remove_all_tags`
- `test_list_tasks_filters_by_tag`
- `test_list_tasks_tag_filter_no_matches_returns_empty_list`
- `test_list_tasks_without_tag_filter_returns_all_tasks`

All 23 pass. No regressions in pre-existing behavior from adding tags.

## 3. Manual browser checks
Performed against the running frontend (`frontend/index.html` + local API):
- Added a tag with excess leading/trailing spaces via the Create Task modal — confirmed it renders trimmed on the card (matches `test_create_task_trims_tags`). See [screenshots/01-create-task-tag-input.png](screenshots/01-create-task-tag-input.png) and [screenshots/02-task-board-tag-tests-overview.png](screenshots/02-task-board-tag-tests-overview.png).
- Removed a previously-added tag via the Edit Task modal and saved — confirmed the tag chip disappeared from the card and other fields (title/description/priority) were unaffected. See [screenshots/03-tag-removed-annotated.png](screenshots/03-tag-removed-annotated.png).
- Applied and cleared the tag filter — confirmed filtered results and empty-state/restore-all behavior matched the backend.

## 4. Behavior contract before/after refactor
No structural refactor was performed for this feature — Tags were added additively (new field + new validator + new optional filter param), so there is no separate before/after contract beyond the full pytest run in section 2, which confirms all pre-existing endpoint behavior (create, list, patch, delete, status transitions) is unchanged with tags present.

## 5. Break Test evidence

### Break Test 1 — case-sensitive duplicate tags on create
**Target assumption:** `validate_tags()` in `app/models.py` prevents duplicate tags on a single task.

**Input:** `POST /tasks {"title": "Case dup test", "tags": ["Backend", "backend"]}`

**Actual result:**
```
status: 201
tags returned: ['Backend', 'backend']
```

**Verdict: Break succeeded.** The dedup check (`if cleaned_tag not in cleaned_tags`) compares exact strings, so `"Backend"` and `"backend"` are treated as different tags and both are kept, even though they'd read as the same label to a user.

### Break Test 2 — case-sensitive tag filter
**Target assumption:** `GET /tasks?tag=...` in `app/storage.py` finds tasks by tag name.

**Input:** Create a task with `tags: ["Backend"]`, then `GET /tasks?tag=backend` (lowercase).

**Actual result:**
```
created task tags: ['Backend']
GET /tasks?tag=backend status: 200
GET /tasks?tag=backend result: []
```

**Verdict: Break succeeded.** The filter (`cleaned_tag in t.tags`) is an exact-match containment check, so a differently-cased filter query returns no results even though a matching tag exists.

This case-sensitivity gap was first spotted manually before being formally run above — see [screenshots/04-case-sensitivity-lowercase-tag.png](screenshots/04-case-sensitivity-lowercase-tag.png), a task deliberately created with a lowercase `"api"` tag to explore whether it would be treated the same as the existing `"API"` tag.

### Decision on both break tests
Per tutor feedback, the requirement was to actually perform and document the break test that had only been identified in passing — not necessarily to fix it. Both are recorded here as **known limitations, left unfixed for this submission**, and are noted in `mini-adr.md`. A future fix would normalize tag comparisons (e.g., compare lowercased) for both dedup and filtering while preserving original casing for display.
