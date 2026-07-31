import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import storage


@pytest.fixture(autouse=True)
def _reset_storage():
    # Run BEFORE every test, never share state across tests.
    storage._reset()
    yield
    storage._reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def created_task(client):
    # Helper: create one ToDo/Medium task and return its dict.
    resp = client.post("/tasks", json={"title": "fixture task"})
    assert resp.status_code == 201
    return resp.json()