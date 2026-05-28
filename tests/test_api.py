import pytest
from httpx import AsyncClient
from src.taskmanager.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/api/health')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'ok'
