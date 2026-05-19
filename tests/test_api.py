"""
Comprehensive test suite for TaskManager API endpoints.

Tests health checks, task operations, error handling, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

from src.taskmanager.main import app


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns basic info."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["db"] == "connected"
    
    def test_docs_endpoint(self, client: TestClient):
        """Test API docs endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestTaskEndpoints:
    """Test task-related endpoints."""
    
    @pytest.fixture
    def sample_task_data(self) -> Dict[str, Any]:
        """Sample task data for testing."""
        return {
            "title": "Test Task",
            "description": "A test task for API testing",
            "priority": "medium",
            "status": "pending"
        }
    
    def test_create_task(self, client: TestClient, sample_task_data: Dict[str, Any]):
        """Test task creation."""
        response = client.post("/api/tasks/", json=sample_task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["priority"] == sample_task_data["priority"]
    
    def test_list_tasks_empty(self, client: TestClient):
        """Test listing tasks when no tasks exist."""
        response = client.get("/api/tasks/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0
    
    def test_get_task_by_id(self, client: TestClient, sample_task_data: Dict[str, Any]):
        """Test getting a specific task by ID."""
        # Create a task first
        create_response = client.post("/api/tasks/", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Get the task
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id


class TestTaskValidation:
    """Test task validation and error handling."""
    
    def test_create_task_invalid_title(self, client: TestClient):
        """Test task creation with invalid title."""
        invalid_data = {
            "title": "",  # Empty title
            "priority": "invalid_priority"  # Invalid priority
        }
        response = client.post("/api/tasks/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_task_missing_required_field(self, client: TestClient):
        """Test task creation with missing required field."""
        invalid_data = {
            "description": "Only description, no title"
            # Missing required "title" field
        }
        response = client.post("/api/tasks/", json=invalid_data)
        assert response.status_code == 422  # Validation error


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])