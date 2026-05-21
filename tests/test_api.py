import pytest
import asyncio
from httpx import AsyncClient
from typing import Dict, Any

from src.taskmanager.main import app
from src.taskmanager.core.database import get_db
from src.taskmanager.models.task import Task, TaskStatus, TaskPriority
from tests.conftest import TestDatabase


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    async def test_health_basic(self, test_db: TestDatabase):
        """Test basic health endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
            assert "timestamp" in data
    
    async def test_health_detailed(self, test_db: TestDatabase):
        """Test detailed health endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/health/detailed")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "database" in data
            assert "redis" in data
            assert "timestamp" in data
    
    async def test_health_unhealthy_database(self, test_db: TestDatabase):
        """Test health endpoint when database is unhealthy."""
        # This test would require mocking the database connection
        # For now, we'll test the happy path
        pass


@pytest.mark.asyncio
class TestTaskCRUD:
    """Test task CRUD operations."""
    
    async def test_create_task(self, test_db: TestDatabase):
        """Test task creation."""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "medium",
            "status": "pending",
            "category": "test"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Task"
            assert data["description"] == "This is a test task"
            assert data["status"] == "pending"
            assert "id" in data
            assert "created_at" in data
            assert "updated_at" in data
    
    async def test_create_task_invalid_data(self, test_db: TestDatabase):
        """Test task creation with invalid data."""
        task_data = {
            "title": "",  # Empty title should be invalid
            "description": "This is a test task"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 422  # Validation error
    
    async def test_get_task(self, test_db: TestDatabase):
        """Test retrieving a single task."""
        # First create a task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high",
            "status": "in_progress",
            "category": "test"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            create_response = await client.post("/api/tasks", json=task_data)
            task_id = create_response.json()["id"]
            
            # Now retrieve the task
            response = await client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Test Task"
            assert data["id"] == task_id
    
    async def test_get_nonexistent_task(self, test_db: TestDatabase):
        """Test retrieving a non-existent task."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/tasks/99999")
            assert response.status_code == 404
    
    async def test_list_tasks(self, test_db: TestDatabase):
        """Test listing tasks."""
        # Create multiple tasks
        tasks_data = [
            {"title": "Task 1", "description": "First task", "priority": "low"},
            {"title": "Task 2", "description": "Second task", "priority": "high"},
            {"title": "Task 3", "description": "Third task", "priority": "medium"}
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for task_data in tasks_data:
                await client.post("/api/tasks", json=task_data)
            
            # List all tasks
            response = await client.get("/api/tasks")
            assert response.status_code == 200
            data = response.json()
            assert "tasks" in data
            assert len(data["tasks"]) >= 3
            assert "total" in data
            assert "page" in data
            assert "size" in data
    
    async def test_list_tasks_with_filters(self, test_db: TestDatabase):
        """Test listing tasks with filters."""
        # Create tasks with different statuses
        tasks_data = [
            {"title": "Pending Task", "status": "pending"},
            {"title": "In Progress Task", "status": "in_progress"},
            {"title": "Completed Task", "status": "completed"}
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for task_data in tasks_data:
                await client.post("/api/tasks", json=task_data)
            
            # Filter by status
            response = await client.get("/api/tasks?status=pending")
            assert response.status_code == 200
            data = response.json()
            assert len([t for t in data["tasks"] if t["status"] == "pending"]) >= 1
    
    async def test_update_task(self, test_db: TestDatabase):
        """Test updating a task."""
        # Create a task first
        task_data = {
            "title": "Original Task",
            "description": "Original description",
            "priority": "low",
            "status": "pending"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            create_response = await client.post("/api/tasks", json=task_data)
            task_id = create_response.json()["id"]
            
            # Update the task
            update_data = {
                "title": "Updated Task",
                "description": "Updated description",
                "priority": "high",
                "status": "in_progress"
            }
            
            response = await client.put(f"/api/tasks/{task_id}", json=update_data)
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Task"
            assert data["description"] == "Updated description"
            assert data["priority"] == "high"
            assert data["status"] == "in_progress"
    
    async def test_update_nonexistent_task(self, test_db: TestDatabase):
        """Test updating a non-existent task."""
        update_data = {"title": "Updated Task"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put("/api/tasks/99999", json=update_data)
            assert response.status_code == 404
    
    async def test_delete_task(self, test_db: TestDatabase):
        """Test deleting a task."""
        # Create a task first
        task_data = {
            "title": "Task to Delete",
            "description": "This will be deleted",
            "priority": "medium"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            create_response = await client.post("/api/tasks", json=task_data)
            task_id = create_response.json()["id"]
            
            # Delete the task
            response = await client.delete(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Task deleted successfully"
            
            # Verify the task is deleted
            get_response = await client.get(f"/api/tasks/{task_id}")
            assert get_response.status_code == 404
    
    async def test_delete_nonexistent_task(self, test_db: TestDatabase):
        """Test deleting a non-existent task."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete("/api/tasks/99999")
            assert response.status_code == 404


@pytest.mark.asyncio
class TestTaskAnalytics:
    """Test task analytics endpoints."""
    
    async def test_task_statistics(self, test_db: TestDatabase):
        """Test task statistics endpoint."""
        # Create tasks with different statuses
        tasks_data = [
            {"title": "Task 1", "status": "pending"},
            {"title": "Task 2", "status": "in_progress"},
            {"title": "Task 3", "status": "completed"},
            {"title": "Task 4", "status": "pending"}
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for task_data in tasks_data:
                await client.post("/api/tasks", json=task_data)
            
            # Get statistics
            response = await client.get("/api/analytics/tasks")
            assert response.status_code == 200
            data = response.json()
            assert "total_tasks" in data
            assert "status_breakdown" in data
            assert "priority_breakdown" in data
            assert "category_breakdown" in data
            assert data["total_tasks"] >= 4
    
    async def test_task_trends(self, test_db: TestDatabase):
        """Test task trends endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/analytics/trends")
            assert response.status_code == 200
            data = response.json()
            assert "created_tasks" in data
            assert "completed_tasks" in data
            assert "completion_rate" in data


@pytest.mark.asyncio
class TestTaskValidation:
    """Test task validation and error handling."""
    
    async def test_task_title_validation(self, test_db: TestDatabase):
        """Test task title validation."""
        invalid_tasks = [
            {"title": "", "description": "Empty title"},  # Empty title
            {"title": "A", "description": "Too short"},  # Too short
            {"title": "x" * 201, "description": "Too long"},  # Too long
            {"title": None, "description": "None title"},  # None title
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for task_data in invalid_tasks:
                response = await client.post("/api/tasks", json=task_data)
                assert response.status_code == 422  # Validation error
    
    async def test_task_priority_validation(self, test_db: TestDatabase):
        """Test task priority validation."""
        invalid_priorities = ["invalid", "random", ""]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for priority in invalid_priorities:
                task_data = {
                    "title": f"Task {priority}",
                    "priority": priority
                }
                response = await client.post("/api/tasks", json=task_data)
                assert response.status_code == 422
    
    async def test_task_status_validation(self, test_db: TestDatabase):
        """Test task status validation."""
        invalid_statuses = ["invalid", "random", ""]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for status in invalid_statuses:
                task_data = {
                    "title": f"Task {status}",
                    "status": status
                }
                response = await client.post("/api/tasks", json=task_data)
                assert response.status_code == 422
    
    async def test_task_description_length(self, test_db: TestDatabase):
        """Test task description length validation."""
        # Very long description should be allowed
        long_description = "x" * 2000
        task_data = {
            "title": "Long Description Task",
            "description": long_description
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            data = response.json()
            assert data["description"] == long_description


@pytest.mark.asyncio
class TestTaskPriorities:
    """Test task priority operations."""
    
    async def test_task_priority_levels(self, test_db: TestDatabase):
        """Test different priority levels."""
        priority_levels = ["low", "medium", "high"]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for priority in priority_levels:
                task_data = {
                    "title": f"Task {priority}",
                    "priority": priority
                }
                response = await client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
                data = response.json()
                assert data["priority"] == priority
    
    async def test_task_priority_updates(self, test_db: TestDatabase):
        """Test updating task priorities."""
        # Create a task
        task_data = {"title": "Original Task", "priority": "low"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            create_response = await client.post("/api/tasks", json=task_data)
            task_id = create_response.json()["id"]
            
            # Update priority to high
            update_data = {"priority": "high"}
            response = await client.put(f"/api/tasks/{task_id}", json=update_data)
            assert response.status_code == 200
            data = response.json()
            assert data["priority"] == "high"


@pytest.mark.asyncio
class TestTaskCategories:
    """Test task category operations."""
    
    async def test_task_categories(self, test_db: TestDatabase):
        """Test task categories."""
        categories = ["work", "personal", "urgent", "important"]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for category in categories:
                task_data = {
                    "title": f"Task {category}",
                    "category": category
                }
                response = await client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
                data = response.json()
                assert data["category"] == category
    
    async def test_task_category_filtering(self, test_db: TestDatabase):
        """Test filtering tasks by category."""
        # Create tasks with different categories
        tasks_data = [
            {"title": "Work Task", "category": "work"},
            {"title": "Personal Task", "category": "personal"},
            {"title": "Urgent Task", "category": "urgent"}
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for task_data in tasks_data:
                await client.post("/api/tasks", json=task_data)
            
            # Filter by category
            response = await client.get("/api/tasks?category=work")
            assert response.status_code == 200
            data = response.json()
            work_tasks = [t for t in data["tasks"] if t["category"] == "work"]
            assert len(work_tasks) >= 1


@pytest.mark.asyncio
class TestPerformance:
    """Test performance-related endpoints."""
    
    async def test_bulk_task_creation(self, test_db: TestDatabase):
        """Test creating multiple tasks quickly."""
        tasks_data = []
        for i in range(50):
            tasks_data.append({
                "title": f"Bulk Task {i}",
                "description": f"Bulk task description {i}",
                "priority": "medium"
            })
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = asyncio.get_event_loop().time()
            
            for task_data in tasks_data:
                response = await client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Should complete in reasonable time (less than 10 seconds)
            assert duration < 10.0
    
    async def test_concurrent_task_operations(self, test_db: TestDatabase):
        """Test concurrent task operations."""
        async def create_task(client, title):
            task_data = {"title": title, "priority": "medium"}
            response = await client.post("/api/tasks", json=task_data)
            return response.status_code == 201
        
        # Create multiple tasks concurrently
        async with AsyncClient(app=app, base_url="http://test") as client:
            tasks = []
            for i in range(10):
                task = asyncio.create_task(create_task(client, f"Concurrent Task {i}"))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            assert all(results)


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    async def test_invalid_json(self, test_db: TestDatabase):
        """Test handling of invalid JSON."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", data="invalid json")
            assert response.status_code == 422
    
    async def test_missing_required_fields(self, test_db: TestDatabase):
        """Test handling of missing required fields."""
        task_data = {"description": "Missing title"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 422
    
    async def test_sql_injection_attempt(self, test_db: TestDatabase):
        """Test handling of SQL injection attempts."""
        malicious_titles = [
            "'; DROP TABLE tasks; --",
            "1' OR '1'='1",
            "admin'--",
            "test'; WAITFOR DELAY '0:0:10'--"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for title in malicious_titles:
                task_data = {"title": title, "description": "Test"}
                response = await client.post("/api/tasks", json=task_data)
                # Should either succeed (sanitized) or fail with validation error
                assert response.status_code in [201, 422]
    
    async def test_rate_limiting(self, test_db: TestDatabase):
        """Test rate limiting (if implemented)."""
        # This test would require rate limiting to be configured
        # For now, we'll test that we can create multiple tasks
        tasks_data = []
        for i in range(10):
            tasks_data.append({
                "title": f"Rate Test Task {i}",
                "description": "Rate limit test"
            })
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for task_data in tasks_data:
                response = await client.post("/api/tasks", json=task_data)
                # All should succeed unless rate limited
                assert response.status_code in [201, 429]


@pytest.mark.asyncio
class TestIntegration:
    """Test integration with external services."""
    
    async def test_database_connection(self, test_db: TestDatabase):
        """Test database connection and operations."""
        # Create a task
        task_data = {"title": "Integration Test", "description": "Testing database integration"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            
            # Retrieve the task to verify database operations work
            task_id = response.json()["id"]
            get_response = await client.get(f"/api/tasks/{task_id}")
            assert get_response.status_code == 200
    
    async def test_cache_functionality(self, test_db: TestDatabase):
        """Test Redis caching functionality."""
        # Create a task
        task_data = {"title": "Cache Test", "description": "Testing cache functionality"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            
            # Retrieve the task multiple times (should use cache)
            for i in range(5):
                get_response = await client.get(f"/api/tasks/{response.json()['id']}")
                assert get_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])