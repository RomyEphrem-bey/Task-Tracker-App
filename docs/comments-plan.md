# Comments on Tasks - Repo-Grounded Plan

The application already supports task comments, but the current contract is
`id`, `text`, and `created_at`. This plan aligns that implementation with the
requested `id`, `task_id`, `author`, `body`, and `created_at` contract without
adding authentication, a database, or dependencies.

## 1. Data Model

- Update `Comment` in `task-tracker-api/app/models.py` so its response fields
  are `id: str`, `task_id: str`, `author: str`, `body: str`, and
  `created_at: datetime`. Keeping `id` as a string follows `TaskResponse`, while
  generating it from `uuid4()` follows the existing comment and task pattern.
- Replace the `text` field in `CommentCreate` with required `author` and `body`
  fields. Reject unknown fields with the existing `ConfigDict(extra="forbid")`
  pattern so clients cannot submit `id`, `task_id`, or `created_at`.
- Strip surrounding whitespace and validate the resulting values as 1-100
  characters for `author` and 1-2000 characters for `body`. This follows the
  existing field-validator pattern used for task titles and comment text.
- Continue storing `comments: list[Comment]` on `TaskResponse` with a
  `default_factory=list`. This preserves the existing task response structure
  and comment-count behavior in the frontend.
- Treat `id`, `task_id`, and `created_at` as server-managed values:
  `task_id` comes from the route path, `id` comes from `uuid4()`, and
  `created_at` comes from `datetime.now(timezone.utc)`.

## 2. API Routes

- Keep `POST /tasks/{task_id}/comments`, accepting only `author` and `body`,
  returning the complete `Comment`, and retaining `201 Created`. This follows
  the existing `add_comment` route's `response_model`, status-code, tag, and
  storage-delegation pattern.
- Keep `GET /tasks/{task_id}/comments`, returning `list[Comment]` in insertion
  order. This follows the current list route and storage list behavior.
- Keep `DELETE /tasks/{task_id}/comments/{comment_id}` and its empty
  `204 No Content` response because deletion already exists and removing it
  would be an unrelated API regression.
- Preserve the current `404` behavior: the route layer converts a missing task
  or comment result from storage into `HTTPException`, following the task and
  comment routes already in `app/main.py`.
- Keep the comment routes in `app/main.py` for this change because that is
  where all existing task and comment routes live. Moving them to an
  `APIRouter` like the health route should be a separate refactor.
- Do not accept `task_id` from the request body; deriving it from the path
  prevents a body/path mismatch.

## 3. Tests

- Update `tests/test_comments.py` using the existing `client` and
  `created_task` fixtures from `tests/conftest.py`; the autouse `_reset_storage`
  fixture should continue isolating every test.
- Update successful creation assertions to verify `author`, `body`, matching
  `task_id`, a UUID-parseable string `id`, and a timezone-aware UTC
  `created_at`.
- Add boundary coverage for author lengths 1 and 100 and body lengths 1 and
  2000, plus rejection tests for missing, blank, and over-limit values.
- Verify surrounding whitespace behavior explicitly for both user-supplied
  fields so the tests document whether limits apply after trimming.
- Verify that extra client fields such as `id`, `task_id`, `created_at`, and
  legacy `text` are rejected with `422`, following the existing unknown-field
  tests for tasks.
- Retain and update the existing list tests for insertion order, empty lists,
  and missing tasks, and retain delete tests for success, missing tasks, and
  missing comments.
- Add a regression assertion that comments returned inside a task response use
  the same new shape as the dedicated comments endpoint, and that deleting a
  task makes its nested comments unreachable.
- No frontend test framework is visible in the files reviewed, so record
  manual browser checks for creating, displaying, counting, and deleting
  comments unless frontend automation is introduced separately.

## 4. Frontend Changes

- Extend the existing comments section in the task edit modal with a required
  author input and a required body textarea. Add `maxlength="100"` and
  `maxlength="2000"` for immediate feedback, while keeping server validation
  authoritative.
- Rename the current `new-comment-text` state and payload handling to the new
  `author` and `body` contract, and continue posting to the existing nested
  comments URL.
- Update `renderComments` to display escaped author and body values and a
  readable UTC timestamp. Continue using `escapeHtml` for every value inserted
  into template HTML.
- Preserve the existing local task-state update after creation/deletion so the
  modal list and board comment-count pill refresh without a full reload.
- Expand client-side empty/length feedback for both fields, reuse
  `getServerErrorMessage` for API validation responses, clear the form only
  after a successful request, and prevent duplicate submissions while a
  request is pending.
- Manually verify keyboard submission, modal reopening, long-body wrapping,
  error recovery, and the existing mobile breakpoints.

## 5. Migration or Storage Notes

- No database migration is needed: `app/storage.py` uses the process-local
  `_tasks` dictionary and stores comments inside each `TaskResponse`.
- Existing in-memory comments use `text` and will disappear on process restart,
  as all current task data does. No durable JSON loading or database migration
  path is visible in the files reviewed.
- Update comment creation in storage to copy the route's `task_id` into each
  comment and to copy validated `author` and `body` from `CommentCreate`.
- Keep comments nested under their task. The current `delete_task` operation
  therefore removes the task and its comments together without a separate
  cascade or orphan cleanup.
- Decide whether adding or deleting a comment should refresh the parent task's
  `updated_at`; the current comment storage operations do not change it.
- Do not add a database, authentication, or dependencies, in accordance with
  the Module 5 repository rules.

## 6. Open Questions

- Is replacing `text` with `body` an intentional breaking API change, or must
  legacy clients receive a compatibility period?
- Should comments remain embedded in every `TaskResponse`, or should task
  responses eventually expose only a count and require the dedicated list
  route? The current API and frontend depend on embedded comments.
- Because authentication is out of scope, is `author` intentionally
  free-form, and should the UI remember the last entered author locally?
- Should whitespace be trimmed before enforcing both length limits, matching
  current title/comment behavior?
- Should adding or deleting a comment update the task's `updated_at`?
- Is comment editing intentionally out of scope?
- Should list order remain oldest-first, as it is now, or become newest-first?
- What timestamp format and timezone presentation should the frontend show
  while the API continues returning UTC?

## 7. My Critique

### Data Model

- TODO

### API Routes

- TODO

### Tests

- TODO

### Frontend Changes

- TODO

### Migration or Storage Notes

- TODO

### Open Questions

- TODO

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** TODO
**Plan I would hand to a teammate:** TODO
**Where the generic plan was still useful:** TODO
**Where repo grounding mattered most:** TODO
