"""
Task management API endpoint tests for TaskManager.

This module contains comprehensive tests for the /api/tasks endpoints,
including CRUD operations, filtering, pagination, and analytics.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, date


class TestTaskCRUD:
    """Test suite for task CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, client: AsyncClient, sample_task_data):
        """Test successful task creation."""
        response = await client.post("/api/tasks", json=sample_task_data)
        
        # Assert response
        assert response.status_code == 201
        data = response.json()
        
        # Assert response structure
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "priority" in data
        assert "status" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Assert values
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["priority"] == sample_task_data["priority"]
        assert data["status"] == sample_task_data["status"]
        assert data["created_at"] == data["updated_at"]  # Should be same on creation
    
    @pytest.mark.asyncio
    async def test_create_task_minimal_data(self, client: AsyncClient):
        """Test task creation with minimal required data."""
        minimal_data = {"title": "Minimal Task"}
        response = await client.post("/api/tasks", json=minimal_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["priority"] == "medium"  # Default value
        assert data["status"] == "pending"    # Default value
    
    @pytest.mark.asyncio
    async def test_create_task_invalid_data(self, client: AsyncClient):
        """Test task creation with invalid data."""
        # Test missing title
        response = await client.post("/api/tasks", json={"description": "No title"})
        assert response.status_code == 422  # Validation error
        
        # Test empty title
        response = await client.post("/api/tasks", json={"title": ""})
        assert response.status_code == 422
        
        # Test invalid priority
        response = await client.post("/api/tasks", json={
            "title": "Invalid Priority",
            "priority": "invalid"
        })
        assert response.status_code == 422
        
        # Test invalid status
        response = await client.post("/api/tasks", json={
            "title": "Invalid Status",
            "status": "invalid"
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_task_success(self, client: AsyncClient, sample_task_data):
        """Test successful task retrieval."""
        # First create a task
        create_response = await client.post("/api/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Then get it
        response = await client.get(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task_data["title"]
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting non-existent task."""
        response = await client.get("/api/tasks/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_task_success(self, client: AsyncClient, sample_task_data, task_update_data):
        """Test successful task update."""
        # Create a task first
        create_response = await client.post("/api/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Update it
        response = await client.put(f"/api/tasks/{task_id}", json=task_update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == task_update_data["title"]
        assert data["description"] == task_update_data["description"]
        assert data["priority"] == task_update_data["priority"]
        assert data["status"] == task_update_data["status"]
        assert data["updated_at"] != data["created_at"]  # Should be different
    
    @pytest.mark.asyncio
    async def test_update_task_partial(self, client: AsyncClient, sample_task_data):
        """Test partial task update."""
        # Create a task first
        create_response = await client.post("/api/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Update only title
        update_data = {"title": "Updated Title Only"}
        response = await client.put(f"/api/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title Only"
        assert data["description"] == sample_task_data["description"]  # Unchanged
        assert data["priority"] == sample_task_data["priority"]      # Unchanged
    
    @pytest.mark.asyncio
    async def test_update_task_not_found(self, client: AsyncClient, task_update_data):
        """Test updating non-existent task."""
        response = await client.put("/api/tasks/99999", json=task_update_data)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, client: AsyncClient, sample_task_data):
        """Test successful task deletion."""
        # Create a task first
        create_response = await client.post("/api/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Delete it
        response = await client.delete(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully"
        
        # Verify it's gone
        get_response = await client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client: AsyncClient):
        """Test deleting non-existent task."""
        response = await client.delete("/api/tasks/99999")
        assert response.status_code == 404


class TestTaskList:
    """Test suite for task listing and filtering."""
    
    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client: AsyncClient):
        """Test listing tasks when none exist."""
        response = await client.get("/api/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 10
        assert data["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_data(self, client: AsyncClient, multiple_tasks_data):
        """Test listing tasks with data."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # List all tasks
        response = await client.get("/api/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 3
        assert data["total"] == 3
        assert data["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_list_tasks_pagination(self, client: AsyncClient, multiple_tasks_data):
        """Test task list pagination."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # Test first page
        response = await client.get("/api/tasks?skip=0&limit=2")
        data = response.json()
        assert len(data["tasks"]) == 2
        assert data["total"] == 3
        assert data["has_more"] is True
        
        # Test second page
        response = await client.get("/api/tasks?skip=2&limit=2")
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["total"] == 3
        assert data["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_list_tasks_priority_filter(self, client: AsyncClient, multiple_tasks_data):
        """Test task filtering by priority."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # Filter by high priority
        response = await client.get("/api/tasks?priority=high")
        data = response.json()
        
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["priority"] == "high"
        assert data["total"] == 1
    
    @pytest.mark.asyncio
    async def test_list_tasks_status_filter(self, client: AsyncClient, multiple_tasks_data):
        """Test task filtering by status."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # Filter by completed status
        response = await client.get("/api/tasks?status=completed")
        data = response.json()
        
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["status"] == "completed"
        assert data["total"] == 1
    
    @pytest.mark.asyncio
    async def test_list_tasks_combined_filters(self, client: AsyncClient, multiple_tasks_data):
        """Test task filtering with multiple criteria."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # Filter by priority and status
        response = await client.get("/api/tasks?priority=medium&status=in_progress")
        data = response.json()
        
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["priority"] == "medium"
        assert data["tasks"][0]["status"] == "in_progress"


class TestTaskAnalytics:
    """Test suite for task analytics endpoints."""
    
    @pytest.mark.asyncio
    async def test_task_analytics_endpoint(self, client: AsyncClient, multiple_tasks_data):
        """Test task analytics endpoint."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # Get analytics
        response = await client.get("/api/tasks/analytics/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Assert analytics structure
        assert "overview" in data
        assert "top_priority_tasks" in data
        assert "recent_completed_tasks" in data
        assert "upcoming_due_tasks" in data
        assert "productivity_score" in data
        assert "recommendations" in data
        
        # Assert overview metrics
        overview = data["overview"]
        assert "total_tasks" in overview
        assert "completed_tasks" in overview
        assert "pending_tasks" in overview
        assert "in_progress_tasks" in overview
        assert "overdue_tasks" in overview
        assert "completed_percentage" in overview
        assert "average_completion_time" in overview
        assert "tasks_by_priority" in overview
        assert "tasks_by_status" in overview
        assert "tasks_by_category" in overview
        assert "productivity_trend" in overview


class TestTaskSpecialEndpoints:
    """Test suite for special task endpoints."""
    
    @pytest.mark.asyncio
    async def test_prioritize_tasks_endpoint(self, client: AsyncClient, multiple_tasks_data):
        """Test AI-powered task prioritization endpoint."""
        # Create multiple tasks
        for task_data in multiple_tasks_data:
            await client.post("/api/tasks", json=task_data)
        
        # Run prioritization
        response = await client.post("/api/tasks/prioritize")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "prioritized_count" in data
        assert "timestamp" in data
        assert data["message"] == "Task prioritization completed"
        assert isinstance(data["prioritized_count"], int)
    
    @pytest.mark.asyncio
    async def test_suggest_tasks_endpoint(self, client: AsyncClient):
        """Test AI-powered task suggestions endpoint."""
        response = await client.post("/api/tasks/suggest")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "suggestions" in data
        assert "timestamp" in data
        assert isinstance(data["suggestions"], list)


class TestTaskEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_create_task_long_title(self, client: AsyncClient):
        """Test task creation with very long title."""
        long_title = "x" * 200  # Max length
        response = await client.post("/api/tasks", json={
            "title": long_title,
            "description": "Task with maximum length title"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == long_title
    
    @pytest.mark.asyncio
    async def test_create_task_long_description(self, client: AsyncClient):
        """Test task creation with very long description."""
        long_description = "x" * 2000  # Max length
        response = await client.post("/api/tasks", json={
            "title": "Task with long description",
            "description": long_description
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == long_description
    
    @pytest.mark.asyncio
    async def test_list_tasks_invalid_pagination(self, client: AsyncClient):
        """Test list tasks with invalid pagination parameters."""
        # Test negative skip
        response = await client.get("/api/tasks?skip=-1")
        assert response.status_code == 422
        
        # Test limit > 100
        response = await client.get("/api/tasks?limit=101")
        assert response.status_code == 422
        
        # Test limit < 1
        response = await client.get("/api/tasks?limit=0")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_task_id_validation(self, client: AsyncClient, sample_task_data):
        """Test task ID validation in various endpoints."""
        # Create a task
        create_response = await client.post("/api/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Test invalid IDs
        invalid_ids = ["abc", -1, 0, None, 3.14]
        for invalid_id in invalid_ids:
            # Test get
            response = await client.get(f"/api/tasks/{invalid_id}")
            assert response.status_code == 422
            
            # Test update
            response = await client.put(f"/api/tasks/{invalid_id}", json={"title": "test"})
            assert response.status_code == 422
            
            # Test delete
            response = await client.delete(f"/api/tasks/{invalid_id}")
            assert response.status_code == 422