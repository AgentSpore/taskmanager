import pytest
from fastapi.testclient import TestClient
from src.taskmanager.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_task():
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "A test task", "completed": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "A test task"
    assert data["completed"] == False
    task_id = data["id"]
    # Clean up
    client.delete(f"/api/tasks/{task_id}")
    return task_id

def test_get_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_task():
    # First create a task
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task 2", "description": "Another test task", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    task_id = data["id"]
    # Get the task
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task 2"
    # Clean up
    client.delete(f"/api/tasks/{task_id}")

def test_update_task():
    # Create a task
    response = client.post(
        "/api/tasks",
        json={"title": "Task to Update", "description": "Original description", "completed": False},
    )
    assert response.status_code == 200
    data = response.json()
    task_id = data["id"]
    # Update the task
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Task", "description": "Updated description", "completed": True},
    )
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["title"] == "Updated Task"
    assert updated_data["description"] == "Updated description"
    assert updated_data["completed"] == True
    # Clean up
    client.delete(f"/api/tasks/{task_id}")

def test_delete_task():
    # Create a task
    response = client.post(
        "/api/tasks",
        json={"title": "Task to Delete", "description": "To be deleted", "completed": False},
    )
    assert response.status_code == 200
    data = response.json()
    task_id = data["id"]
    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    # Verify it's gone
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404

def test_create_category():
    response = client.post(
        "/api/categories",
        json={"name": "Test Category", "description": "A test category"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    category_id = data["id"]
    # Clean up
    client.delete(f"/api/categories/{category_id}")
    return category_id

def test_get_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_category():
    # Create a category
    response = client.post(
        "/api/categories",
        json={"name": "Test Category 2", "description": "Another test category"},
    )
    assert response.status_code == 200
    data = response.json()
    category_id = data["id"]
    # Get the category
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Category 2"
    # Clean up
    client.delete(f"/api/categories/{category_id}")

def test_update_category():
    # Create a category
    response = client.post(
        "/api/categories",
        json={"name": "Category to Update", "description": "Original description"},
    )
    assert response.status_code == 200
    data = response.json()
    category_id = data["id"]
    # Update the category
    response = client.put(
        f"/api/categories/{category_id}",
        json={"name": "Updated Category", "description": "Updated description"},
    )
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["name"] == "Updated Category"
    assert updated_data["description"] == "Updated description"
    # Clean up
    client.delete(f"/api/categories/{category_id}")

def test_delete_category():
    # Create a category
    response = client.post(
        "/api/categories",
        json={"name": "Category to Delete", "description": "To be deleted"},
    )
    assert response.status_code == 200
    data = response.json()
    category_id = data["id"]
    # Delete the category
    response = client.delete(f"/api/categories/{category_id}")
    assert response.status_code == 200
    # Verify it's gone
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 404