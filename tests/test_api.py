import pytest
from fastapi.testclient import TestClient
from src.taskmanager.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_create_task():
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

def test_get_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_task():
    # First create a task
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test description"},
    )
    assert response.status_code == 200
    task_id = response.json()["id"]
    # Get the task
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"

def test_update_task():
    # Create a task
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test description"},
    )
    assert response.status_code == 200
    task_id = response.json()["id"]
    # Update the task
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Task", "description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated description"

def test_delete_task():
    # Create a task
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test description"},
    )
    assert response.status_code == 200
    task_id = response.json()["id"]
    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    # Check it's gone
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404

def test_create_category():
    response = client.post(
        "/api/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert "id" in data

def test_get_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_category():
    # Create a category
    response = client.post(
        "/api/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 200
    category_id = response.json()["id"]
    # Get the category
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Test Category"

def test_update_category():
    # Create a category
    response = client.post(
        "/api/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 200
    category_id = response.json()["id"]
    # Update the category
    response = client.put(
        f"/api/categories/{category_id}",
        json={"name": "Updated Category"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"

def test_delete_category():
    # Create a category
    response = client.post(
        "/api/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 200
    category_id = response.json()["id"]
    # Delete the category
    response = client.delete(f"/api/categories/{category_id}")
    assert response.status_code == 200
    # Check it's gone
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 404