"""
Health endpoint tests for TaskManager.

This module contains comprehensive tests for the /api/health endpoint,
including status checks, database connectivity, and response validation.
"""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI


class TestHealthEndpoint:
    """Test suite for the health endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_basic(self, client: AsyncClient):
        """Test basic health endpoint functionality."""
        response = await client.get("/api/health")
        
        # Assert response status
        assert response.status_code == 200
        
        # Assert response structure
        data = response.json()
        assert "status" in data
        assert "db" in data
        assert "uptime_seconds" in data
        assert "requests_served" in data
        
        # Assert response values
        assert data["status"] == "healthy"
        assert data["db"] == "connected"
        assert isinstance(data["uptime_seconds"], int)
        assert isinstance(data["requests_served"], int)
        assert data["requests_served"] >= 0
    
    @pytest.mark.asyncio  
    async def test_health_endpoint_response_format(self, client: AsyncClient):
        """Test that health endpoint returns properly formatted JSON."""
        response = await client.get("/api/health")
        
        # Assert content type
        assert response.headers["content-type"] == "application/json"
        
        # Assert response is valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # Assert all required fields are present
        required_fields = ["status", "db", "uptime_seconds", "requests_served"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    @pytest.mark.asyncio
    async def test_health_endpoint_multiple_requests(self, client: AsyncClient):
        """Test health endpoint behavior under multiple requests."""
        # Make multiple requests
        responses = []
        for i in range(5):
            response = await client.get("/api/health")
            responses.append(response)
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
        
        # Request counter should increment
        first_count = responses[0].json()["requests_served"]
        last_count = responses[-1].json()["requests_served"]
        assert last_count > first_count
    
    @pytest.mark.asyncio
    async def test_health_endpoint_with_invalid_methods(self, client: AsyncClient):
        """Test health endpoint with HTTP methods it shouldn't accept."""
        # Test POST (should fail)
        response = await client.post("/api/health")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test PUT (should fail)
        response = await client.put("/api/health")
        assert response.status_code == 405
        
        # Test DELETE (should fail)
        response = await client.delete("/api/health")
        assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_health_endpoint_performance(self, client: AsyncClient):
        """Test health endpoint response time."""
        import time
        
        start_time = time.time()
        response = await client.get("/api/health")
        end_time = time.time()
        
        # Response should be fast (less than 1 second)
        response_time = end_time - start_time
        assert response_time < 1.0, f"Health endpoint too slow: {response_time}s"
        
        # Response should still be successful
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_health_endpoint_consistency(self, client: AsyncClient):
        """Test that health endpoint returns consistent data."""
        # Make two requests
        response1 = await client.get("/api/health")
        response2 = await client.get("/api/health")
        
        # Both should have same status and db connection
        assert response1.json()["status"] == response2.json()["status"]
        assert response1.json()["db"] == response2.json()["db"]
        
        # Request counter should be different (incrementing)
        assert response2.json()["requests_served"] > response1.json()["requests_served"]
    
    @pytest.mark.asyncio
    async def test_health_endpoint_cors_headers(self, client: AsyncClient):
        """Test that health endpoint includes proper CORS headers."""
        response = await client.get("/api/health")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers


class TestHealthIntegration:
    """Integration tests for health endpoint with other components."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_with_app_startup(self, client: AsyncClient):
        """Test health endpoint works after app startup."""
        # This is implicitly tested by the fixture, but we can verify
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_endpoint_middleware_interaction(self, client: AsyncClient):
        """Test that health endpoint works with middleware."""
        # Make a request to health endpoint
        response = await client.get("/api/health")
        
        # Verify middleware is working (request counter should be > 0)
        data = response.json()
        assert data["requests_served"] > 0