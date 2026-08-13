# Release Evidence

## Baseline
- Branch: final-project
- Date: 2026-08-12
- Local app run command: `uvicorn app.main:app --port 8000`
- /health result: `200 {"status":"ok","timestamp":"2026-08-12T10:01:29.057965+00:00"}`
- Frontend check: served `frontend/` via `python -m http.server 5500`, opened `http://localhost:5500/index.html` — Kanban board and create/edit flow confirmed visible and working.
- Test command: `pytest -q`
- Test result: `39 passed, 3 warnings in 0.37s` (33 pre-existing + 6 added for the description/assignee/tag/comment-length security fix)

## CI evidence
- Workflow file: `.github/workflows/ci.yml`
- Triggers on both `push` (all branches) and `pull_request` (target: main) — confirmed by reading the workflow file.
- Latest push run: https://github.com/RomyEphrem-bey/Task-Tracker-App/actions/runs/31593697074 (commit `1ee07ec`, conclusion: success)
- Latest pull_request run: https://github.com/RomyEphrem-bey/Task-Tracker-App/actions/runs/31591114587 (commit `ac79dc7`, conclusion: success)
- Test command used by CI: `pytest -v --tb=short` (working directory: `task-tracker-api`)
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped, dependencies are installed before tests run, Python version is pinned (`3.11`) not vague
- Intentional red-run evidence: N/A — not produced during Module 4 (checked `docs/midcourse/` and Module 5 docs; no deliberate break-test exercise found, only a real accidental CI failure from a missing dependency, later fixed in `1b7ea27`)

## Docker evidence
- Build command: `docker build -t task-tracker:dev task-tracker-api`
- Run command: `docker run -d --name task-tracker-dev -p 8000:8000 task-tracker:dev`
- /health check: `200 {"status":"ok","timestamp":"2026-08-12T10:38:12.338362+00:00"}`
- Non-root check: confirmed — container runs as `app` (uid=1000, gid=1000), verified via `docker exec task-tracker-dev whoami`
- No-baked-secrets check: confirmed — `/app` contains only the `app/` code directory (no `.env`, `tests/`, `docs/`); no secret-like files found; container env vars are standard Python/base-image vars only

## Documentation claim-vs-reality log
| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `task-tracker-api/README.md` said "Prerequisites: Python 3.12+" | Compared against `.github/workflows/ci.yml` (`python-version: '3.11'`) and `Dockerfile` (`FROM python:3.11-slim`) | Mismatch — CI and Docker actually run on 3.11, not 3.12+ | Corrected README prerequisite to "Python 3.11+" |
| `CLAUDE.md`/README claim: "Direct ToDo → Done ... rejected with 422" | Ran the live app: `POST /tasks` (status `ToDo`) then `PATCH` to `status: Done` | Match — returned `422` with `"Invalid status transition from ToDo to Done..."` | None |
| `task-tracker-api/README.md` claim: `GET /tasks` supports optional `tag` query filter | Ran the live app: created a task tagged `backend`, called `GET /tasks?tag=backend` | Match — response contained only the matching task | None |
