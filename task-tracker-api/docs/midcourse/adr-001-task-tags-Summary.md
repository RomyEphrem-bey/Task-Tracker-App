ADR-001: Task Tags
Architecture A - Tags embedded directly in each task
Status	Proposed	Date	31 July 2026
Scope	Tags feature only	Decision owner	 QA

--> Context
The existing task tracker uses FastAPI, Pydantic, in-memory storage, and a vanilla HTML/CSS/JavaScript frontend. The requested feature adds optional task tags, tag editing, validation, display, and filtering without changing unrelated behavior.
--> Decision
Store tags directly on each task as a list of trimmed strings. No separate tag entity, endpoint, database, or new runtime dependency will be introduced.
--> Tech stack
Area	Technology
API	FastAPI 0.115.12
Validation	Pydantic 2.11.4
Server	Uvicorn 0.34.2
Frontend	Existing vanilla HTML, CSS, and JavaScript
Testing	Existing Pytest and FastAPI TestClient setup
--> Files to modify
app/models.py: Add tags to create, update, and response models. Trim values, reject whitespace-only tags with 422, allow an empty list, and prevent duplicates within a task.
app/storage.py: Save tags during creation, replace them only when supplied in PATCH, support removing all tags with an empty list, and optionally filter tasks by exact tag.
app/main.py: Add an optional tag query parameter to the existing GET /tasks endpoint.
frontend/index.html: Add tag inputs to Create/Edit modals, tag chips on cards, and a clearable tag filter while keeping Kanban columns and existing empty states.
tests/test_tasks.py: Cover tagged and untagged creation, trimming, 422 validation, PATCH add/replace/remove behavior, field preservation, and filtering.
tests/conftest.py: Only extend fixtures if needed for tagged tasks; no structural change expected.
README.md: Document the tags field, validation rules, PATCH behavior, and GET /tasks?tag=... usage.
--> Data model sketch
Task
- id: string
- title: string
- description: string
- status: TaskStatus
- priority: TaskPriority
- assignee: string | null
- tags: list[string] = []
- created_at: datetime
- updated_at: datetime
--> Required behavior
•	Create: tags may be omitted; omitted tags are stored as an empty list.
•	Validation: "  Backend  " becomes "Backend"; a whitespace-only tag returns 422.
•	PATCH: omitted tags remain unchanged; tags: [] removes all tags; a supplied list replaces the current tags.
•	Display: each tag appears as a separate chip; tasks without tags show no empty chip or placeholder.
•	Filter: GET /tasks?tag=Backend returns matching tasks; clearing the filter restores all tasks and never changes stored data.
--> Consequences
This decision satisfies the five requested user stories with minimal changes, preserves existing create/edit behavior, keeps tags optional, and avoids adding unrequested infrastructure or features.
