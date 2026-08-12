## Final Project

Branch reviewed: final-project

For full local setup (venv, dependencies, `.env`), see [task-tracker-api/README.md](task-tracker-api/README.md).

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally
From `task-tracker-api/` (after setup):
```
uvicorn app.main:app --reload --port 8000
```

### How to run tests
From `task-tracker-api/`:
```
pytest -q
```

### How to run with Docker
```
docker build -t task-tracker:dev task-tracker-api
docker run -d --name task-tracker-dev -p 8000:8000 task-tracker:dev
curl http://localhost:8000/health
```

### Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary
AI helped draft or review: security fix, CI evidence, Docker verification, docs.
I verified the work by: running the pytest suite, checking `/health`, manually confirming the frontend in a browser, inspecting the running Docker container, and scanning the repo for secrets.
One AI suggestion I rejected or corrected: the security review's suggestion to add authentication to fix anonymous API access — rejected because adding authentication is a new product feature forbidden by this final project's scope rules; see docs/final-ai-review.md.
