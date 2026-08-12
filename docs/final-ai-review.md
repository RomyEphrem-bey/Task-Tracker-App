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
Checked whether the repo contains real secrets, credentials, or personal/customer data, per the course's "No real secrets or personal data" rule — this was a manual check, not just re-reading the AI security review, since that review didn't cover this risk.

What I checked:
- Whether `.env` (or any file with a secret/credential/token-like name) was ever committed, in the current tree or full git history — it was not; only `.env.example` (non-sensitive: `PORT`, `APP_ENV`) is tracked, and `.env` is excluded via `.gitignore` at both the repo root and `task-tracker-api/`.
- All tracked files for common secret patterns (API keys, AWS keys, `sk-`/`ghp_` tokens, private-key headers, hardcoded passwords) and for real-looking email addresses — no matches.
- `Dockerfile` and `.github/workflows/ci.yml` for baked-in secrets or `.env` being copied into the image — neither does.

Result: no real secrets, credentials, or personal/customer data found in the repo. The only "password/token/secret/credential" mentions are in `docs/ai-playbook.md`, where they're the user's own written non-negotiable rules, not leaked data.

## One AI output I rejected or corrected
TODO — to be completed during Part C.

## Three AI usage rules
1. Never paste:
2. Always verify:
3. Record AI contributions by:

## Ownership statement
TODO — to be completed at the end of the project.
