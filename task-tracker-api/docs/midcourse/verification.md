# Verification

## Feature 1: Tags / Labels

### 1. Baseline check
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

## Feature 2: Task Comments

### Backend test results
Full suite run: `python -m pytest tests/ -v`

```
33 passed, 3 warnings in 0.85s
```

23 tests from Feature 1 (unchanged) + 10 new Task Comments tests in `tests/test_comments.py`:
- `test_add_comment_returns_201_with_comment_body`
- `test_add_comment_trims_whitespace`
- `test_add_comment_blank_returns_422`
- `test_add_comment_missing_task_returns_404`
- `test_list_comments_returns_all_for_task_in_order`
- `test_list_comments_empty_task_returns_empty_list`
- `test_list_comments_missing_task_returns_404`
- `test_delete_comment_returns_204_and_removes_it`
- `test_delete_comment_missing_task_returns_404`
- `test_delete_comment_missing_comment_returns_404`

All 33 pass. No regressions in pre-existing task or tag behavior from adding comments.

### Break Test — deliberately weakening blank-comment validation
Unlike the Tags break tests (which probed an existing, unfixed gap with adversarial input), this break test targets the test suite's own reliability: temporarily breaking the implementation to confirm the test that guards it actually fails when it should.

**Target assumption:** `test_add_comment_blank_returns_422` in `tests/test_comments.py` correctly catches a regression if blank-comment rejection is ever removed from `CommentCreate`.

**Action:** Temporarily edited `app/models.py`'s `_text_not_blank` validator to remove the blank-rejection check:
```python
@field_validator("text")
@classmethod
def _text_not_blank(cls, v: str) -> str:
    v2 = v.strip()
    return v2
```

**Actual result:** Running `pytest tests/test_comments.py::test_add_comment_blank_returns_422` against the weakened validator:
```
assert 201 == 422
 +  where 201 = <Response [201 Created]>.status_code
1 failed, 3 warnings in 0.42s
```

**Verdict: Break succeeded, then reverted.** The test failed exactly as expected once the validation it protects was removed — a blank comment was accepted with `201` instead of rejected with `422`. This confirms the test is meaningful (it would catch a real regression), not a false positive. The validator was immediately restored to its original form, and the full suite was re-run to confirm all 33 tests pass again.
