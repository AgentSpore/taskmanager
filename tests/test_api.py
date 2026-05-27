import pytest
from httpx import AsyncClient
from src.taskmanager.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "db" in data
        assert "uptime_seconds" in data
        assert "requests_served" in data

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/tasks", json={
            "title": "Test Task",
            "description": "Test description",
            "priority": 3,
            "due_date": "2026-06-01T00:00:00Z"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test description"
        assert data["priority"] == 3
        assert "id" in data

@pytest.mark.asyncio
async def test_get_tasks():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_task_by_id():
    # First create a task
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post("/api/tasks", json={
            "title": "Test Task 2",
            "description": "Test description 2",
            "priority": 1
        })
        assert create_response.status_code == 200
        task_id = create_response.json()["id"]
        
        # Then get it
        response = await client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task 2"

@pytest.mark.asyncio
async def test_update_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create
        create_response = await client.post("/api/tasks", json={
            "title": "Task to update",
            "description": "Original description",
            "priority": 2
        })
        task_id = create_response.json()["id"]
        
        # Update
        update_response = await client.put(f"/api/tasks/{task_id}", json={
            "title": "Updated Task",
            "description": "Updated description",
            "priority": 4
        })
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated description"
        assert data["priority"] == 4

@pytest.mark.asyncio
async def test_delete_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create
        create_response = await client.post("/api/tasks", json={
            "title": "Task to delete",
            "description": "Will be deleted",
            "priority": 5
        })
        task_id = create_response.json()["id"]
        
        # Delete
        delete_response = await client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_response = await client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_task_analytics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/tasks/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "pending_tasks" in data
