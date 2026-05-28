import pytest
from httpx import AsyncClient
from src.taskmanager.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"title": "Test Task", "description": "Test description"}
        r = await ac.post("/api/tasks", json=payload)
    assert r.status_code == 200
    task = r.json()
    assert task["title"] == "Test Task"
    assert task["description"] == "Test description"

@pytest.mark.asyncio
async def test_get_tasks():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list)
