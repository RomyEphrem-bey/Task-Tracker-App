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
- Latest run: https://github.com/RomyEphrem-bey/Task-Tracker-App/actions/runs/31589404512 (run #13, commit `9b531ef`, conclusion: success)
- Test command used by CI: `pytest -v --tb=short` (working directory: `task-tracker-api`)
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped, dependencies are installed before tests run

## Docker evidence
- Build command: `docker build -t task-tracker:dev task-tracker-api`
- Run command: `docker run -d --name task-tracker-dev -p 8000:8000 task-tracker:dev`
- /health check: `200 {"status":"ok","timestamp":"2026-08-12T10:38:12.338362+00:00"}`
- Non-root check: confirmed — container runs as `app` (uid=1000, gid=1000), verified via `docker exec task-tracker-dev whoami`
- No-baked-secrets check: confirmed — `/app` contains only the `app/` code directory (no `.env`, `tests/`, `docs/`); no secret-like files found; container env vars are standard Python/base-image vars only

## Documentation claim-vs-reality log
TODO — to be completed during Part B.
