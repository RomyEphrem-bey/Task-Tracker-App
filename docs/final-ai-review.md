# Final AI Review and Ownership Evidence

## AGENTS.md guardrails
- Repo-specific stack and commands included: yes — Stack (Python 3.11, FastAPI, Pydantic v2, pytest, vanilla JS) and Run/test commands (`uvicorn app.main:app --reload`, `pytest -v`) sections.
- Docs-first/read-first guardrail included: yes — "Prefer read-only analysis first" and "Explain what files you read before giving a repo-grounded answer."
- Unexpected app/frontend edits rule included: yes — added final-project-scoped rule: "Only change app/ or frontend/ for a small bug fix, security fix, or documentation-supported correction (final project ground rule)."

## AI code review mini-log
Reviewed diff: commit `9b531ef` ("Add length/count validation limits to prevent unbounded-input DoS"), file `app/models.py`.

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| `_description_max_length` and `_assignee_max_length` are duplicated verbatim between `TaskCreate` (lines 73-85) and `TaskUpdate` (lines 115-127) — extract into a shared validator, the way `validate_tags` already is. | Useful | True duplication, and the codebase already has a precedent for extracting shared validation logic (`validate_tags`). Not a bug, but a legitimate simplification. | Confirmed by reading `app/models.py` — the two blocks are byte-for-byte identical. Not applied (low priority, out of scope for this fix), but the observation is valid. |
| Consider adding docstrings to the new field validators (`_description_max_length`, `_assignee_max_length`) for consistency with `validate_tags`. | Noise | Style-only nit with no effect on correctness or security. Also doesn't match actual project convention — sibling validators like `_title_not_blank` and `_text_not_blank` (pre-existing, not part of this diff) also have no docstrings, so this isn't even an inconsistency. | Checked the other `@field_validator` methods in `app/models.py`; none have docstrings. No change made. |
| The comment-length check at line 155 (`if len(v2) > 1000`) measures the raw input, not the stripped value — padding with whitespace could bypass the 1000-character cap. | Wrong | Misreads the code. `v2 = v.strip()` happens first (line 152), and the length check is against `v2`, not the raw `v` — stripped whitespace cannot be used to bypass the cap. | Re-read `app/models.py` lines 149-157 to confirm `v2` (not `v`) is what's checked. No change made. |

## AI security mini-review
| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| Unbounded input on `description`, `assignee`, tags, and comment text permits memory exhaustion. | `app/models.py` (pre-fix, only `title` capped); originally flagged in `docs/security-review.md` row 1. | Valid | No length/count limits existed outside `title`; genuine DoS-shaped risk if the API were reachable by untrusted clients. | Fixed: added length/count limits in `app/models.py` (description ≤2000, assignee ≤100, tag ≤50 chars/≤20 tags per task, comment text ≤1000), covered by 6 new tests (`tests/test_tasks.py`, `tests/test_comments.py`). Overall task/comment *count* growth is still open — tracked as backlog item 1 in `docs/security-review.md`. |
| CORS allows the opaque `null` origin plus wildcard methods/headers. | `app/main.py` lines 30-40 — `allow_origins` includes `"null"`, `allow_methods=["*"]`, `allow_headers=["*"]`, `allow_credentials=False`; originally flagged in `docs/security-review.md` row 3. | Valid (Low severity) | Confirmed by reading the actual middleware config — the `null` origin and wildcard lists are real. `allow_credentials=False` limits real-world impact today; this only becomes dangerous if credentialed auth is added later. | No change made — acceptable for local/course-scope use; tighten to exact origins/methods before any real deployment. |
| CI Actions are pinned to mutable major-version tags, not commit SHAs. | `.github/workflows/ci.yml` — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4` (tag-pinned, not SHA-pinned); `python -m pip install --upgrade pip` pulls an unpinned pip version; originally flagged in `docs/security-review.md` row 5. | Noise | Technically accurate, but disproportionate for this project's actual risk profile — a local, single-student course repo with no secrets, no publish step, and no real supply-chain attack surface. SHA-pinning is enterprise-hardening advice that doesn't change anything meaningful here. | No change; already tracked as a low-priority backlog item in `docs/security-review.md` if this were ever deployed for real. |

## Manual security check
Checked whether the repo contains real secrets, credentials, or personal/customer data, per the course's "No real secrets or personal data" rule — this was a manual check, not just re-reading the AI security review, since that review didn't cover this risk.

What I checked:
- Whether `.env` (or any file with a secret/credential/token-like name) was ever committed, in the current tree or full git history — it was not; only `.env.example` (non-sensitive: `PORT`, `APP_ENV`) is tracked, and `.env` is excluded via `.gitignore` at both the repo root and `task-tracker-api/`.
- All tracked files for common secret patterns (API keys, AWS keys, `sk-`/`ghp_` tokens, private-key headers, hardcoded passwords) and for real-looking email addresses — no matches.
- `Dockerfile` and `.github/workflows/ci.yml` for baked-in secrets or `.env` being copied into the image — neither does.

Result: no real secrets, credentials, or personal/customer data found in the repo. The only "password/token/secret/credential" mentions are in `docs/ai-playbook.md`, where they're the user's own written non-negotiable rules, not leaked data.

### Additional manual/exploratory checks (live app, QA-style black-box testing)

**Boundary-value testing on the input validation limits** — sent requests at exactly the documented limit and one unit past it for each field, against the live API:

| Field | At limit | Over limit |
|---|---|---|
| title (200 chars) | 200 chars → `201` | 201 chars → `422` |
| description (2000 chars) | 2000 chars → `201` | 2001 chars → `422` |
| tags (20 max) | 20 tags → `201` | 21 tags → `422` |
| comment text (1000 chars) | 1000 chars → `201` | 1001 chars → `422` |

All limits are enforced exactly as documented — no off-by-one gaps.

**Error-message information-disclosure check** — triggered an invalid enum value, malformed JSON, a missing required field, and a nonexistent task ID against the live API. All four returned clean, structured error bodies (standard FastAPI/Pydantic validation errors, or a plain `{"detail":"Task not found"}`) with no stack traces, internal file paths, or debug info in any response.

**Exploratory browser test of drag-and-drop** — opened `frontend/index.html` in a real browser and dragged cards between columns:
- An initial `404` error ("Unable to update task — The server returned HTTP 404") was traced to a stale browser tab left open since before an earlier backend restart — in-memory storage is documented as lost on restart, so the card's ID no longer existed server-side. Reloading the page removed the stale card and confirmed this was a testing artifact, not a live defect. Notably, the optimistic-update/rollback UI correctly reverted the card and showed a clear error even for this unexpected `404`, not just the `422` case it was originally written for.
- Confirmed live that an invalid status transition (`InProgress → ToDo`) is rejected with `422` and the UI correctly rolls the card back, matching `app/business_rules.py`'s transition whitelist.
- **New usability finding** (not previously flagged by the AI review): with a longer task list, dragging a card does not auto-scroll the column when dragged toward its top/bottom edge, so columns or cards scrolled out of view are unreachable by drag alone. Documented as a finding, not fixed — frontend changes are restricted to small, justified bug/security fixes under this project's ground rules, and this is a minor UX gap rather than a functional or security defect.

## One AI output I rejected or corrected
The AI security review (`docs/security-review.md` row 2, `app/main.py:48`) suggested adding authentication plus per-resource authorization to fix anonymous access to all task/comment routes. I rejected this fix as-is: the final project's ground rules explicitly forbid adding authentication ("No new product features"), and anonymous access is an intentional, already-accepted scope decision for this local/teaching environment, not a defect. Instead of applying the fix, I kept the finding documented as an accepted, course-scoped risk (graded "Valid, fix out of scope") with a note that real authentication would be required before any actual deployment.

## Three AI usage rules
1. Never paste: credentials, tokens, `.env` values, or real personal/customer data into an AI tool or this repo — confirmed none exist in the repo via the manual security check above.
2. Always verify: run the actual test suite, hit the live endpoints, or read the exact lines before accepting an AI claim — this is what caught the AI code review's "Wrong" comment (the whitespace-bypass claim) instead of taking it at face value.
3. Record AI contributions by: grading every AI review comment and security finding in a table (Useful/Noise/Wrong, Valid/False Positive/Noise) with a stated reason, so what AI said and what I decided are both on the record — not just "AI helped."

## Ownership statement
I'm comfortable submitting this repo as my own work because I verified AI suggestions against the running app rather than accepting them blindly. I personally tested boundary limits, error handling, and drag-and-drop behavior live, catching issues the AI review missed. I rejected one AI suggestion (adding authentication) because it violated this project's scope rules. Every fix and finding here reflects a decision I made and can explain.
