from fastapi.testclient import TestClient


# POST /tasks/{task_id}/comments
def test_add_comment_returns_201_with_comment_body(client: TestClient, created_task):
    r = client.post(
        f"/tasks/{created_task['id']}/comments",
        json={"text": "Looks good to me"},
    )

    assert r.status_code == 201
    body = r.json()
    assert body["text"] == "Looks good to me"
    assert "id" in body and len(body["id"]) > 0
    assert "created_at" in body


def test_add_comment_trims_whitespace(client: TestClient, created_task):
    r = client.post(
        f"/tasks/{created_task['id']}/comments",
        json={"text": "  needs review  "},
    )

    assert r.status_code == 201
    assert r.json()["text"] == "needs review"


def test_add_comment_blank_returns_422(client: TestClient, created_task):
    r = client.post(
        f"/tasks/{created_task['id']}/comments",
        json={"text": "   "},
    )

    assert r.status_code == 422


def test_add_comment_text_over_1000_chars_returns_422(client: TestClient, created_task):
    r = client.post(
        f"/tasks/{created_task['id']}/comments",
        json={"text": "x" * 1001},
    )

    assert r.status_code == 422


def test_add_comment_missing_task_returns_404(client: TestClient):
    r = client.post("/tasks/missing/comments", json={"text": "hello"})

    assert r.status_code == 404


# GET /tasks/{task_id}/comments
def test_list_comments_returns_all_for_task_in_order(client: TestClient, created_task):
    client.post(f"/tasks/{created_task['id']}/comments", json={"text": "first"})
    client.post(f"/tasks/{created_task['id']}/comments", json={"text": "second"})

    r = client.get(f"/tasks/{created_task['id']}/comments")

    assert r.status_code == 200
    texts = [c["text"] for c in r.json()]
    assert texts == ["first", "second"]


def test_list_comments_empty_task_returns_empty_list(client: TestClient, created_task):
    r = client.get(f"/tasks/{created_task['id']}/comments")

    assert r.status_code == 200
    assert r.json() == []


def test_list_comments_missing_task_returns_404(client: TestClient):
    r = client.get("/tasks/missing/comments")

    assert r.status_code == 404


# DELETE /tasks/{task_id}/comments/{comment_id}
def test_delete_comment_returns_204_and_removes_it(client: TestClient, created_task):
    add_response = client.post(
        f"/tasks/{created_task['id']}/comments",
        json={"text": "temporary comment"},
    )
    comment_id = add_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{created_task['id']}/comments/{comment_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = client.get(f"/tasks/{created_task['id']}/comments")
    assert list_response.json() == []


def test_delete_comment_missing_task_returns_404(client: TestClient):
    r = client.delete("/tasks/missing/comments/whatever")

    assert r.status_code == 404


def test_delete_comment_missing_comment_returns_404(client: TestClient, created_task):
    r = client.delete(f"/tasks/{created_task['id']}/comments/missing-comment-id")

    assert r.status_code == 404
