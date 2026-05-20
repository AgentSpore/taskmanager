"""
Comprehensive API tests for TaskManager application.

This test suite covers all API endpoints including:
- Health checks
- Task CRUD operations
- Category management
- Error handling
- Integration tests
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient
from datetime import datetime, date
from typing import Dict, Any

# Import the FastAPI app
from src.taskmanager.main import app

# Test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test basic health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TaskManager"
        assert data["version"] == "0.1.0"
        assert "uptime_seconds" in data
        assert "requests_served" in data
        assert "timestamp" in data
    
    def test_detailed_health_check(self):
        """Test detailed health endpoint."""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "system" in data
        assert "cpu_percent" in data["system"]
        assert "memory_rss" in data["system"]
    
    def test_ping_endpoint(self):
        """Test ping endpoint."""
        response = client.get("/api/ping")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "pong"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data


class TestTaskEndpoints:
    """Test task management endpoints."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.test_task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "medium",
            "status": "pending",
            "tags": ["test", "api"],
            "estimated_hours": 2
        }
    
    def test_create_task(self):
        """Test task creation."""
        response = client.post("/api/tasks/", json=self.test_task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == self.test_task_data["title"]
        assert data["description"] == self.test_task_data["description"]
        assert data["priority"] == self.test_task_data["priority"]
        assert data["status"] == self.test_task_data["status"]
        assert data["tags"] == self.test_task_data["tags"]
        assert data["estimated_hours"] == self.test_task_data["estimated_hours"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_minimal(self):
        """Test task creation with minimal data."""
        minimal_data = {"title": "Minimal Task"}
        response = client.post("/api/tasks/", json=minimal_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["priority"] == "medium"  # default
        assert data["status"] == "pending"  # default
        assert data["tags"] == []  # default
    
    def test_list_tasks(self):
        """Test listing tasks."""
        # Create a task first
        client.post("/api/tasks/", json=self.test_task_data)
        
        response = client.get("/api/tasks/")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert "has_more" in data
        assert len(data["tasks"]) >= 1
        assert data["total"] >= 1
    
    def test_list_tasks_with_filters(self):
        """Test listing tasks with filters."""
        # Create tasks with different priorities
        task_high = {"title": "High Priority Task", "priority": "high"}
        task_low = {"title": "Low Priority Task", "priority": "low"}
        
        client.post("/api/tasks/", json=task_high)
        client.post("/api/tasks/", json=task_low)
        
        # Filter by high priority
        response = client.get("/api/tasks/?priority=high")
        assert response.status_code == 200
        
        data = response.json()
        assert all(task["priority"] == "high" for task in data["tasks"])
    
    def test_get_task(self):
        """Test getting a specific task."""
        # Create a task
        create_response = client.post("/api/tasks/", json=self.test_task_data)
        task_id = create_response.json()["id"]
        
        # Get the task
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == self.test_task_data["title"]
    
    def test_get_nonexistent_task(self):
        """Test getting a non-existent task."""
        response = client.get("/api/tasks/99999")
        assert response.status_code == 404
    
    def test_update_task(self):
        """Test updating a task."""
        # Create a task
        create_response = client.post("/api/tasks/", json=self.test_task_data)
        task_id = create_response.json()["id"]
        
        # Update the task
        update_data = {"title": "Updated Task", "priority": "high"}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["priority"] == "high"
        assert data["id"] == task_id
    
    def test_update_nonexistent_task(self):
        """Test updating a non-existent task."""
        response = client.put("/api/tasks/99999", json={"title": "Updated"})
        assert response.status_code == 404
    
    def test_delete_task(self):
        """Test deleting a task."""
        # Create a task
        create_response = client.post("/api/tasks/", json=self.test_task_data)
        task_id = create_response.json()["id"]
        
        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        
        # Verify task is deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_task(self):
        """Test deleting a non-existent task."""
        response = client.delete("/api/tasks/99999")
        assert response.status_code == 404
    
    def test_task_analytics(self):
        """Test task analytics endpoint."""
        response = client.get("/api/tasks/analytics/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "top_priority_tasks" in data
        assert "recent_completed_tasks" in data
        assert "upcoming_due_tasks" in data
        assert "productivity_score" in data
        assert "recommendations" in data
        
        # Check overview structure
        overview = data["overview"]
        assert "total_tasks" in overview
        assert "completed_tasks" in overview
        assert "pending_tasks" in overview
        assert "in_progress_tasks" in overview
        assert "overdue_tasks" in overview
        assert "completed_percentage" in overview
    
    def test_task_prioritize_endpoint(self):
        """Test task prioritization endpoint."""
        response = client.post("/api/tasks/prioritize")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "prioritized_count" in data
        assert "timestamp" in data
    
    def test_task_suggest_endpoint(self):
        """Test task suggestions endpoint."""
        response = client.post("/api/tasks/suggest")
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data
        assert "timestamp" in data


class TestCategoryEndpoints:
    """Test category management endpoints."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.test_category_data = {
            "name": "Test Category",
            "description": "This is a test category",
            "color": "#007bff"
        }
    
    def test_create_category(self):
        """Test category creation."""
        response = client.post("/api/categories/", json=self.test_category_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == self.test_category_data["name"]
        assert data["description"] == self.test_category_data["description"]
        assert data["color"] == self.test_category_data["color"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_category_minimal(self):
        """Test category creation with minimal data."""
        minimal_data = {"name": "Minimal Category"}
        response = client.post("/api/categories/", json=minimal_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Minimal Category"
        assert data["description"] is None
        assert data["color"] == "#007bff"  # default
    
    def test_list_categories(self):
        """Test listing categories."""
        # Create a category first
        client.post("/api/categories/", json=self.test_category_data)
        
        response = client.get("/api/categories/")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert len(data["categories"]) >= 1
        assert data["total"] >= 1
    
    def test_get_category(self):
        """Test getting a specific category."""
        # Create a category
        create_response = client.post("/api/categories/", json=self.test_category_data)
        category_id = create_response.json()["id"]
        
        # Get the category
        response = client.get(f"/api/categories/{category_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == self.test_category_data["name"]
    
    def test_get_nonexistent_category(self):
        """Test getting a non-existent category."""
        response = client.get("/api/categories/99999")
        assert response.status_code == 404
    
    def test_update_category(self):
        """Test updating a category."""
        # Create a category
        create_response = client.post("/api/categories/", json=self.test_category_data)
        category_id = create_response.json()["id"]
        
        # Update the category
        update_data = {"name": "Updated Category", "color": "#28a745"}
        response = client.put(f"/api/categories/{category_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Category"
        assert data["color"] == "#28a745"
        assert data["id"] == category_id
    
    def test_update_nonexistent_category(self):
        """Test updating a non-existent category."""
        response = client.put("/api/categories/99999", json={"name": "Updated"})
        assert response.status_code == 404
    
    def test_delete_category(self):
        """Test deleting a category."""
        # Create a category
        create_response = client.post("/api/categories/", json=self.test_category_data)
        category_id = create_response.json()["id"]
        
        # Delete the category
        response = client.delete(f"/api/categories/{category_id}")
        assert response.status_code == 200
        
        # Verify category is deleted
        get_response = client.get(f"/api/categories/{category_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_category(self):
        """Test deleting a non-existent category."""
        response = client.delete("/api/categories/99999")
        assert response.status_code == 404


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_task_data(self):
        """Test creating task with invalid data."""
        # Missing required field (title)
        invalid_data = {"description": "Missing title"}
        response = client.post("/api/tasks/", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Invalid priority
        invalid_data = {"title": "Test", "priority": "invalid_priority"}
        response = client.post("/api/tasks/", json=invalid_data)
        assert response.status_code == 422
    
    def test_invalid_category_data(self):
        """Test creating category with invalid data."""
        # Missing required field (name)
        invalid_data = {"description": "Missing name"}
        response = client.post("/api/categories/", json=invalid_data)
        assert response.status_code == 422
        
        # Invalid color
        invalid_data = {"name": "Test", "color": "invalid_color"}
        response = client.post("/api/categories/", json=invalid_data)
        assert response.status_code == 422
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoints."""
        response = client.get("/api/invalid")
        assert response.status_code == 404
        
        response = client.post("/api/invalid")
        assert response.status_code == 404


class TestIntegration:
    """Integration tests for multiple operations."""
    
    def test_task_category_integration(self):
        """Test task-category relationship."""
        # Create a category
        category_data = {"name": "Integration Test", "color": "#ffc107"}
        category_response = client.post("/api/categories/", json=category_data)
        category_id = category_response.json()["id"]
        
        # Create a task with the category
        task_data = {
            "title": "Categorized Task",
            "category_id": category_id,
            "priority": "high"
        }
        task_response = client.post("/api/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        # Verify task has category
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 200
        
        task = get_response.json()
        assert task["category_id"] == category_id
        
        # List tasks by category
        list_response = client.get(f"/api/tasks/?category_id={category_id}")
        assert list_response.status_code == 200
        
        tasks = list_response.json()
        assert len(tasks["tasks"]) >= 1
        assert tasks["tasks"][0]["category_id"] == category_id
    
    def test_bulk_operations(self):
        """Test multiple operations in sequence."""
        # Create multiple tasks
        task1 = client.post("/api/tasks/", json={"title": "Task 1", "priority": "high"})
        task2 = client.post("/api/tasks/", json={"title": "Task 2", "priority": "low"})
        
        assert task1.status_code == 201
        assert task2.status_code == 201
        
        # List all tasks
        list_response = client.get("/api/tasks/")
        assert list_response.status_code == 200
        
        data = list_response.json()
        assert data["total"] >= 2
        
        # Update one task
        task_id = task1.json()["id"]
        update_response = client.put(f"/api/tasks/{task_id}", json={"status": "completed"})
        assert update_response.status_code == 200
        
        # Verify update
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.json()["status"] == "completed"
        
        # Delete one task
        delete_response = client.delete(f"/api/tasks/{task2.json()['id']}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        list_response = client.get("/api/tasks/")
        data = list_response.json()
        # Should have at least 1 task (the updated one)
        assert data["total"] >= 1


class TestAPIDocumentation:
    """Test API documentation and OpenAPI schema."""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert len(schema["paths"]) >= 1
    
    def test_swagger_docs(self):
        """Test Swagger UI endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        content = response.text
        assert "swagger" in content.lower()
        assert "openapi" in content.lower()
    
    def test_redoc_docs(self):
        """Test ReDoc UI endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
        
        content = response.text
        assert "redoc" in content.lower()
        assert "openapi" in content.lower()


# Test configuration
pytest_plugins = []


# Test fixtures
@pytest.fixture
def test_task_data():
    """Fixture providing test task data."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium",
        "status": "pending",
        "tags": ["test", "api"],
        "estimated_hours": 2
    }


@pytest.fixture
def test_category_data():
    """Fixture providing test category data."""
    return {
        "name": "Test Category",
        "description": "This is a test category",
        "color": "#007bff"
    }


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )


# Async test support
@pytest.mark.asyncio
async def test_async_health_check():
    """Async test for health check."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"


# Performance tests
class TestPerformance:
    """Performance-related tests."""
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/health")
            results.append(response.status_code)
        
        # Make multiple concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    def test_large_response_handling(self):
        """Test handling of large responses."""
        # Create multiple tasks to test large response
        for i in range(20):
            task_data = {"title": f"Task {i}", "description": f"Description {i}" * 10}
            response = client.post("/api/tasks/", json=task_data)
            assert response.status_code == 201
        
        # Test listing with larger limit
        response = client.get("/api/tasks/?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tasks"]) >= 20


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])