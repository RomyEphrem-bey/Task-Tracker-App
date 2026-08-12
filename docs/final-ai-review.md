# Final AI Review and Ownership Evidence

## AGENTS.md guardrails
- Repo-specific stack and commands included: TODO
- Docs-first/read-first guardrail included: TODO
- Unexpected app/frontend edits rule included: TODO

## AI code review mini-log
| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| | | | |

## AI security mini-review
| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| Unbounded input on `description`, `assignee`, tags, and comment text permits memory exhaustion. | `app/models.py` (pre-fix, only `title` capped); originally flagged in `docs/security-review.md` row 1. | Valid | No length/count limits existed outside `title`; genuine DoS-shaped risk if the API were reachable by untrusted clients. | Fixed: added length/count limits in `app/models.py` (description ≤2000, assignee ≤100, tag ≤50 chars/≤20 tags per task, comment text ≤1000), covered by 6 new tests (`tests/test_tasks.py`, `tests/test_comments.py`). Overall task/comment *count* growth is still open — tracked as backlog item 1 in `docs/security-review.md`. |

## Manual security check
TODO — to be completed during Part C.

## One AI output I rejected or corrected
TODO — to be completed during Part C.

## Three AI usage rules
1. Never paste:
2. Always verify:
3. Record AI contributions by:

## Ownership statement
TODO — to be completed at the end of the project.
