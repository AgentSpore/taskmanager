"""
Category management API endpoint tests for TaskManager.

This module contains comprehensive tests for the /api/categories endpoints,
including CRUD operations and integration with tasks.
"""

import pytest
from httpx import AsyncClient


class TestCategoryCRUD:
    """Test suite for category CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_category_success(self, client: AsyncClient, sample_category_data):
        """Test successful category creation."""
        response = await client.post("/api/categories", json=sample_category_data)
        
        # Assert response
        assert response.status_code == 201
        data = response.json()
        
        # Assert response structure
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "color" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "task_count" in data
        
        # Assert values
        assert data["name"] == sample_category_data["name"]
        assert data["description"] == sample_category_data["description"]
        assert data["color"] == sample_category_data["color"]
        assert data["task_count"] == 0  # Should be 0 on creation
        assert data["created_at"] == data["updated_at"]  # Should be same on creation
    
    @pytest.mark.asyncio
    async def test_create_category_minimal_data(self, client: AsyncClient):
        """Test category creation with minimal required data."""
        minimal_data = {"name": "Minimal Category"}
        response = await client.post("/api/categories", json=minimal_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Category"
        assert data["color"] == "#007bff"  # Default value
    
    @pytest.mark.asyncio
    async def test_create_category_invalid_data(self, client: AsyncClient):
        """Test category creation with invalid data."""
        # Test missing name
        response = await client.post("/api/categories", json={"description": "No name"})
        assert response.status_code == 422  # Validation error
        
        # Test empty name
        response = await client.post("/api/categories", json={"name": ""})
        assert response.status_code == 422
        
        # Test name too long
        long_name = "x" * 101
        response = await client.post("/api/categories", json={"name": long_name})
        assert response.status_code == 422
        
        # Test invalid color (not hex)
        response = await client.post("/api/categories", json={
            "name": "Invalid Color",
            "color": "not-hex"
        })
        assert response.status_code == 422
        
        # Test color wrong length
        response = await client.post("/api/categories", json={
            "name": "Invalid Color Length",
            "color": "#12345"  # Should be 7 chars including #
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(self, client: AsyncClient, sample_category_data):
        """Test category creation with duplicate name."""
        # Create first category
        await client.post("/api/categories", json=sample_category_data)
        
        # Try to create with same name
        response = await client.post("/api/categories", json=sample_category_data)
        
        # Should fail due to unique constraint
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_category_success(self, client: AsyncClient, sample_category_data):
        """Test successful category retrieval."""
        # First create a category
        create_response = await client.post("/api/categories", json=sample_category_data)
        category_id = create_response.json()["id"]
        
        # Then get it
        response = await client.get(f"/api/categories/{category_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == sample_category_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_category_not_found(self, client: AsyncClient):
        """Test getting non-existent category."""
        response = await client.get("/api/categories/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_categories_empty(self, client: AsyncClient):
        """Test listing categories when none exist."""
        response = await client.get("/api/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert data["categories"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_list_categories_with_data(self, client: AsyncClient, sample_category_data):
        """Test listing categories with data."""
        # Create a category
        await client.post("/api/categories", json=sample_category_data)
        
        # List categories
        response = await client.get("/api/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) == 1
        assert data["total"] == 1
    
    @pytest.mark.asyncio
    async def test_update_category_success(self, client: AsyncClient, sample_category_data):
        """Test successful category update."""
        # Create a category first
        create_response = await client.post("/api/categories", json=sample_category_data)
        category_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "name": "Updated Category Name",
            "description": "Updated description",
            "color": "#28a745"
        }
        response = await client.put(f"/api/categories/{category_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["color"] == update_data["color"]
        assert data["updated_at"] != data["created_at"]
    
    @pytest.mark.asyncio
    async def test_update_category_partial(self, client: AsyncClient, sample_category_data):
        """Test partial category update."""
        # Create a category first
        create_response = await client.post("/api/categories", json=sample_category_data)
        category_id = create_response.json()["id"]
        
        # Update only name
        update_data = {"name": "Updated Name Only"}
        response = await client.put(f"/api/categories/{category_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name Only"
        assert data["description"] == sample_category_data["description"]  # Unchanged
        assert data["color"] == sample_category_data["color"]            # Unchanged
    
    @pytest.mark.asyncio
    async def test_update_category_not_found(self, client: AsyncClient):
        """Test updating non-existent category."""
        update_data = {"name": "Non-existent"}
        response = await client.put("/api/categories/99999", json=update_data)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_category_success(self, client: AsyncClient, sample_category_data):
        """Test successful category deletion."""
        # Create a category first
        create_response = await client.post("/api/categories", json=sample_category_data)
        category_id = create_response.json()["id"]
        
        # Delete it
        response = await client.delete(f"/api/categories/{category_id}")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Category deleted successfully"
        
        # Verify it's gone
        get_response = await client.get(f"/api/categories/{category_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, client: AsyncClient):
        """Test deleting non-existent category."""
        response = await client.delete("/api/categories/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_category_with_tasks(self, client: AsyncClient, sample_category_data, sample_task_data):
        """Test deleting category that has tasks."""
        # Create a category
        category_response = await client.post("/api/categories", json=sample_category_data)
        category_id = category_response.json()["id"]
        
        # Create a task with this category
        task_with_category = sample_task_data.copy()
        task_with_category["category_id"] = category_id
        await client.post("/api/tasks", json=task_with_category)
        
        # Try to delete the category (should fail or handle gracefully)
        response = await client.delete(f"/api/categories/{category_id}")
        
        # Depending on implementation, this might succeed with cascade or fail
        # For now, let's assume it succeeds and tasks are handled
        assert response.status_code in [200, 400]


class TestCategoryIntegration:
    """Test suite for category integration with tasks."""
    
    @pytest.mark.asyncio
    async def test_category_task_count_update(self, client: AsyncClient, sample_category_data, sample_task_data):
        """Test that category task_count updates when tasks are added/removed."""
        # Create a category
        category_response = await client.post("/api/categories", json=sample_category_data)
        category_id = category_response.json()["id"]
        
        # Initial task count should be 0
        assert category_response.json()["task_count"] == 0
        
        # Create a task with this category
        task_with_category = sample_task_data.copy()
        task_with_category["category_id"] = category_id
        await client.post("/api/tasks", json=task_with_category)
        
        # Get category again - task_count should be updated
        response = await client.get(f"/api/categories/{category_id}")
        data = response.json()
        assert data["task_count"] == 1
        
        # Delete the task
        tasks_response = await client.get("/api/tasks")
        task_id = tasks_response.json()["tasks"][0]["id"]
        await client.delete(f"/api/tasks/{task_id}")
        
        # Get category again - task_count should be 0
        response = await client.get(f"/api/categories/{category_id}")
        data = response.json()
        assert data["task_count"] == 0
    
    @pytest.mark.asyncio
    async def test_task_category_filtering(self, client: AsyncClient, sample_category_data, sample_task_data):
        """Test filtering tasks by category."""
        # Create a category
        category_response = await client.post("/api/categories", json=sample_category_data)
        category_id = category_response.json()["id"]
        
        # Create a task with this category
        task_with_category = sample_task_data.copy()
        task_with_category["category_id"] = category_id
        await client.post("/api/tasks", json=task_with_category)
        
        # Create another task without category
        await client.post("/api/tasks", json=sample_task_data)
        
        # Filter tasks by category
        response = await client.get(f"/api/tasks?category_id={category_id}")
        data = response.json()
        
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["category_id"] == category_id
        assert data["total"] == 1
    
    @pytest.mark.asyncio
    async def test_category_color_validation(self, client: AsyncClient):
        """Test category color validation thoroughly."""
        test_colors = [
            ("#000000", True),    # Valid black
            ("#ffffff", True),    # Valid white
            ("#ff0000", True),    # Valid red
            ("#00ff00", True),    # Valid green
            ("#0000ff", True),    # Valid blue
            ("#123456", True),    # Valid hex
            ("#abcdef", True),    # Valid hex
            ("#ABCDEF", True),    # Valid hex uppercase
            ("#AbCdEf", True),    # Valid hex mixed case
            ("invalid", False),   # Invalid - missing #
            ("#12345", False),    # Invalid - too short
            ("#1234567", False),  # Invalid - too long
            ("#123g56", False),   # Invalid - contains g
            ("", False),          # Invalid - empty
            ("#", False),         # Invalid - just #
        ]
        
        for color, should_work in test_colors:
            category_data = {
                "name": f"Color Test {color}",
                "color": color
            }
            
            response = await client.post("/api/categories", json=category_data)
            
            if should_work:
                assert response.status_code == 201
                data = response.json()
                assert data["color"] == color.lower()  # Should be normalized to lowercase
            else:
                assert response.status_code == 422


class TestCategoryEdgeCases:
    """Test suite for category edge cases."""
    
    @pytest.mark.asyncio
    async def test_category_name_special_characters(self, client: AsyncClient):
        """Test category names with special characters."""
        special_names = [
            "Test & Category",
            "Test @ Category", 
            "Test # Category",
            "Test $ Category",
            "Test % Category",
            "Test * Category",
            "Test + Category",
            "Test - Category",
            "Test = Category",
            "Test : Category",
            "Test ; Category",
            "Test , Category",
            "Test . Category",
            "Test ? Category",
            "Test ! Category",
            "Test (Category)",
            "Test [Category]",
            "Test {Category}",
            "Test <Category>",
        ]
        
        for name in special_names:
            category_data = {"name": name, "description": f"Test with {name}"}
            response = await client.post("/api/categories", json=category_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == name
    
    @pytest.mark.asyncio
    async def test_category_unicode_names(self, client: AsyncClient):
        """Test category names with unicode characters."""
        unicode_names = [
            "测试类别",  # Chinese
            "カテゴリ", # Japanese
            "카테고리", # Korean
            "категория", # Russian
            "categorie", # French
            "categoría", # Spanish
            "kategorie", # German
        ]
        
        for name in unicode_names:
            category_data = {"name": name, "description": f"Test with {name}"}
            response = await client.post("/api/categories", json=category_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == name
    
    @pytest.mark.asyncio
    async def test_category_description_long_text(self, client: AsyncClient):
        """Test category with very long description."""
        long_description = "x" * 500  # Max length
        category_data = {
            "name": "Long Description Category",
            "description": long_description
        }
        
        response = await client.post("/api/categories", json=category_data)
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == long_description