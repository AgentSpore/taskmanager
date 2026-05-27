import os
import sys
# Set test database URL before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test_taskmanager.db"
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from fastapi.testclient import TestClient
from src.taskmanager.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "db" in data
    assert "uptime_seconds" in data
    assert "requests_served" in data

def test_create_and_get_task():
    # Create a task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "due_date": "2026-12-31T00:00:00Z",
        "category_id": None
    }
    response = client.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    created = response.json()
    task_id = created["id"]
    assert created["title"] == task_data["title"]
    assert created["description"] == task_data["description"]
    assert created["priority"] == task_data["priority"]
    assert created["due_date"] == task_data["due_date"]
    assert created["category_id"] == task_data["category_id"]

    # Get the task
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == task_id
    assert fetched["title"] == task_data["title"]

    # List tasks
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert any(t["id"] == task_id for t in tasks)

    # Update task
    update_data = {"title": "Updated Task", "priority": "medium"}
    response = client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated Task"
    assert updated["priority"] == "medium"
    # Ensure other fields unchanged
    assert updated["description"] == task_data["description"]
    assert updated["due_date"] == task_data["due_date"]

    # Delete task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    # Verify deletion
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404

def test_category_crud():
    # Create category
    cat_data = {"name": "Test Category", "description": "A test category"}
    response = client.post("/api/categories", json=cat_data)
    assert response.status_code == 200
    created = response.json()
    cat_id = created["id"]
    assert created["name"] == cat_data["name"]
    assert created["description"] == cat_data["description"]

    # Get category
    response = client.get(f"/api/categories/{cat_id}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == cat_id
    assert fetched["name"] == cat_data["name"]

    # List categories
    response = client.get("/api/categories")
    assert response.status_code == 200
    cats = response.json()
    assert isinstance(cats, list)
    assert any(c["id"] == cat_id for c in cats)

    # Update category
    update_data = {"name": "Updated Category"}
    response = client.put(f"/api/categories/{cat_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Updated Category"
    assert updated["description"] == cat_data["description"]  # unchanged

    # Delete category
    response = client.delete(f"/api/categories/{cat_id}")
    assert response.status_code == 200
    response = client.get(f"/api/categories/{cat_id}")
    assert response.status_code == 404

def test_task_analytics():
    # Create a couple tasks for analytics
    client.post("/api/tasks", json={"title": "Task 1", "description": "Desc1", "priority": "low"})
    client.post("/api/tasks", json={"title": "Task 2", "description": "Desc2", "priority": "high"})
    response = client.get("/api/tasks/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "completed_tasks" in data
    assert "pending_tasks" in data
    assert "priority_distribution" in data
    # Ensure counts are at least 2
    assert data["total_tasks"] >= 2

def test_error_handling():
    # Non-existent task
    response = client.get("/api/tasks/99999")
    assert response.status_code == 404
    # Invalid task creation
    response = client.post("/api/tasks", json={})
    assert response.status_code == 422  # Validation error
    # Non-existent category
    response = client.get("/api/categories/99999")
    assert response.status_code == 404

# Teardown: remove test database file
import atexit
@atexit.register
def remove_test_db():
    try:
        os.remove("./test_taskmanager.db")
    except FileNotFoundError:
        pass