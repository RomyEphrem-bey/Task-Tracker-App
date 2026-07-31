from fastapi.testclient import TestClient


# POST /tasks
def test_create_task_valid_returns_201_with_full_body(client: TestClient):
    r = client.post("/tasks", json={"title": "Buy milk"})

    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Buy milk"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["description"] == ""
    assert body["assignee"] is None
    assert "id" in body and len(body["id"]) > 0
    assert "created_at" in body and "updated_at" in body


def test_create_task_missing_title_returns_422(client: TestClient):
    r = client.post("/tasks", json={})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": " "})
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "x", "priority": "Urgent"})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "x", "made_up": 1})
    assert r.status_code == 422


# GET /tasks
def test_list_tasks_empty_returns_200_and_empty_list(client: TestClient):
    r = client.get("/tasks")

    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_returns_created_task(client: TestClient, created_task):
    r = client.get("/tasks")

    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == created_task["id"]


# PATCH /tasks
def test_patch_updates_title_only_preserves_description_and_status(
    client: TestClient, created_task
):
    r = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": "updated title"},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "updated title"
    assert body["description"] == ""
    assert body["status"] == "ToDo"


def test_patch_not_found_returns_404(client: TestClient):
    r = client.patch("/tasks/missing", json={"title": "x"})
    assert r.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(
    client: TestClient, created_task
):
    r = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "InProgress"},
    )

    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(
    client: TestClient, created_task
):
    # created_task is ToDo; jumping straight to Done MUST be rejected
    r = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "Done"},
    )

    assert r.status_code == 422
    assert "Invalid status transition" in r.json()["detail"]


# DELETE /tasks
def test_delete_existing_returns_204_no_body(
    client: TestClient, created_task
):
    r = client.delete(f"/tasks/{created_task['id']}")

    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client: TestClient):
    r = client.delete("/tasks/no-such-id")

    assert r.status_code == 404


def test_patch_invalid_transition_inprogress_to_todo_returns_422(
    client: TestClient, created_task
):
    client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "InProgress"},
    )

    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "ToDo"},
    )

    assert response.status_code == 422

    body = response.json()
    assert "Invalid status transition" in body["detail"]