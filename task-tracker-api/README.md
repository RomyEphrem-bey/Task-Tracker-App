# Task Tracker API

A learning-focused REST API built with Python and FastAPI, using in-memory
storage (no database) — all task data is lost on restart.

## Prerequisites

- Python 3.11+

---

## 1. Create a virtual environment and install dependencies

**Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Configure environment variables

Copy the example file and adjust values as needed:

**Linux/macOS**

```bash
cp .env.example .env
```

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
```

---

## 3. Start the server

**Linux/macOS**

```bash
uvicorn app.main:app --reload --port 8000
```

**Windows (PowerShell)**

```powershell
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs (Swagger UI) are at `http://localhost:8000/docs` — every
endpoint there includes a full description, parameters, and example
responses.

---

## 4. Available endpoints

**Tasks**

- `POST /tasks` — create a task
- `GET /tasks` — list tasks (optional query filters: `status`, `priority`, `tag`)
- `GET /tasks/{task_id}` — get a single task
- `PATCH /tasks/{task_id}` — partially update a task (title, description, status, priority, assignee, tags)
- `DELETE /tasks/{task_id}` — delete a task

**Comments** (nested under a task)

- `POST /tasks/{task_id}/comments` — add a comment
- `GET /tasks/{task_id}/comments` — list a task's comments
- `DELETE /tasks/{task_id}/comments/{comment_id}` — delete a comment

**Health**

- `GET /health` — service status and current UTC timestamp

---

## 5. Validation rules

- **Title** — required, cannot be blank, 200 characters or fewer.
- **Description** — optional, 2000 characters or fewer.
- **Assignee** — optional, 100 characters or fewer.
- **Tags** — each tag is trimmed and cannot be blank, 50 characters or fewer, duplicates are removed, and a task can have at most 20 tags.
- **Comment text** — required, cannot be blank, 1000 characters or fewer.

Any request that exceeds these limits is rejected with `422 Unprocessable Entity`.

---

## 6. Test the health endpoint

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{
    "status": "ok",
    "timestamp": "2026-07-27T10:30:00.123456+00:00"
}
```

---

## 7. Run the test suite

```bash
pytest
```

Run a single test:

```bash
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body
```