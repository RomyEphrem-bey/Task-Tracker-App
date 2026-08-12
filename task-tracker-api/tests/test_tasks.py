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

#create task with tags
def test_create_task_with_tags(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "tags": ["Backend", "Regression"],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["tags"] == ["Backend", "Regression"]

#create task without tags:
def test_create_task_without_tags(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Update test notes",
        },
    )

    assert response.status_code == 201
    assert response.json()["tags"] == []

#Trim Tag Values
def test_create_task_trims_tags(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "tags": ["  Backend  ", " Regression "],
        },
    )

    assert response.status_code == 201
    assert response.json()["tags"] == ["Backend", "Regression"]

#reject a whitespace only tag:
def test_create_task_rejects_blank_tag(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "tags": ["   "],
        },
    )

    assert response.status_code == 422

#reject a description over 2000 characters:
def test_create_task_description_over_2000_chars_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "description": "x" * 2001,
        },
    )

    assert response.status_code == 422

#reject an assignee over 100 characters:
def test_create_task_assignee_over_100_chars_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "assignee": "x" * 101,
        },
    )

    assert response.status_code == 422

#reject a tag over 50 characters:
def test_create_task_tag_over_50_chars_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "tags": ["x" * 51],
        },
    )

    assert response.status_code == 422

#reject more than 20 tags:
def test_create_task_more_than_20_tags_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "tags": [f"tag{i}" for i in range(21)],
        },
    )

    assert response.status_code == 422

#reject a patched assignee over 100 characters:
def test_patch_assignee_over_100_chars_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"assignee": "x" * 101},
    )

    assert response.status_code == 422

#update only the tags:
def test_update_only_tags_preserves_other_fields(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "description": "Check valid login",
            "priority": "High",
            "tags": ["Backend"],
        },
    )

    created_task = create_response.json()

    update_response = client.patch(
        f"/tasks/{created_task['id']}",
        json={
            "tags": ["Regression"],
        },
    )

    assert update_response.status_code == 200

    updated_task = update_response.json()
    assert updated_task["tags"] == ["Regression"]
    assert updated_task["title"] == "Test login API"
    assert updated_task["description"] == "Check valid login"
    assert updated_task["priority"] == "High"

#remove All tags:
def test_remove_all_tags(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test login API",
            "tags": ["Backend", "Regression"],
        },
    )

    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={
            "tags": [],
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["tags"] == []

#adding 3 tests to validate the tag filter
def test_list_tasks_filters_by_tag(client: TestClient):
    client.post(
        "/tasks",
        json={"title": "Backend task", "tags": ["Backend"]},
    )
    client.post(
        "/tasks",
        json={"title": "Frontend task", "tags": ["Frontend"]},
    )

    response = client.get("/tasks?tag=Backend")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Backend task"

def test_list_tasks_tag_filter_no_matches_returns_empty_list(
    client: TestClient,
):
    client.post(
        "/tasks",
        json={"title": "Backend task", "tags": ["Backend"]},
    )

    response = client.get("/tasks?tag=Mobile")

    assert response.status_code == 200
    assert response.json() == []

def test_list_tasks_without_tag_filter_returns_all_tasks(
    client: TestClient,
):
    client.post(
        "/tasks",
        json={"title": "Backend task", "tags": ["Backend"]},
    )
    client.post(
        "/tasks",
        json={"title": "Frontend task", "tags": ["Frontend"]},
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2