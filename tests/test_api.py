import pytest
from httpx import AsyncClient
from src.taskmanager.main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health(async_client):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_create_task(async_client):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": "high",
        "due_date": "2026-12-31T00:00:00Z"
    }
    response = await async_client.post("/api/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_tasks(async_client):
    response = await async_client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_task(async_client):
    # First create a task
    task_data = {
        "title": "Test Task 2",
        "description": "Test Description 2",
        "priority": "medium",
        "due_date": "2026-12-31T00:00:00Z"
    }
    create_response = await async_client.post("/api/tasks", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Then get it
    response = await async_client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == task_data["title"]

@pytest.mark.asyncio
async def test_update_task(async_client):
    # Create a task
    task_data = {
        "title": "Task to Update",
        "description": "Original Description",
        "priority": "low",
        "due_date": "2026-12-31T00:00:00Z"
    }
    create_response = await async_client.post("/api/tasks", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Update it
    update_data = {
        "title": "Updated Task",
        "description": "Updated Description",
        "priority": "high",
        "due_date": "2026-12-31T00:00:00Z"
    }
    response = await async_client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

@pytest.mark.asyncio
async def test_delete_task(async_client):
    # Create a task
    task_data = {
        "title": "Task to Delete",
        "description": "Will be deleted",
        "priority": "low",
        "due_date": "2026-12-31T00:00:00Z"
    }
    create_response = await async_client.post("/api/tasks", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Delete it
    response = await async_client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = await async_client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_create_category(async_client):
    category_data = {
        "name": "Test Category",
        "description": "Test Category Description"
    }
    response = await async_client.post("/api/categories", json=category_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_categories(async_client):
    response = await async_client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
