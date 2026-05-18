"""
Test suite for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app

client = TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database connection for testing."""
    with patch('src.taskmanager.core.database.get_db') as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        yield mock_db


class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns basic application info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
        assert "uptime_seconds" in data
        assert data["message"] == "Welcome to TaskManager"
        assert data["version"] == "0.1.0"
        assert data["docs_url"] == "/docs"
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint returns comprehensive status."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = [
            "status", "service", "version", "environment", 
            "database", "uptime_seconds", "requests_served", 
            "timestamp", "checks"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check field values
        assert data["status"] == "healthy"
        assert data["service"] == "TaskManager"
        assert data["version"] == "0.1.0"
        assert "development" in data["environment"]  # Should contain development
        assert data["database"] in ["healthy", "checking"]
        assert isinstance(data["uptime_seconds"], (int, float))
        assert isinstance(data["requests_served"], int)
        assert isinstance(data["timestamp"], (int, float))
        assert isinstance(data["checks"], dict)
        
        # Check specific checks
        checks = data["checks"]
        assert "database" in checks
        assert "cors" in checks
        assert "logging" in checks
    
    def test_detailed_health_check(self):
        """Test the detailed health check returns system information."""
        response = client.get("/api/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = [
            "status", "service", "version", "environment",
            "system", "uptime_seconds", "requests_served",
            "timestamp", "python_version", "platform"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check system information
        system = data["system"]
        assert "cpu_percent" in system
        assert "memory_rss" in system
        assert "memory_vms" in system
        assert "memory_percent" in system
        assert "num_threads" in system
        assert "num_handles" in system
        
        # Check that system values are reasonable
        assert 0 <= system["cpu_percent"] <= 100
        assert system["memory_rss"] >= 0
        assert system["memory_vms"] >= 0
        assert 0 <= system["memory_percent"] <= 100
        assert system["num_threads"] >= 0
        assert system["num_handles"] >= 0
    
    def test_ping_endpoint(self):
        """Test the ping endpoint returns simple response."""
        response = client.get("/api/health/ping")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "timestamp" in data
        assert data["message"] == "pong"
        assert isinstance(data["timestamp"], (int, float))
    
    def test_health_check_with_mock_database_failure(self, mock_db):
        """Test health check handles database failure gracefully."""
        # Mock database to raise an exception
        mock_db.__aenter__.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/health")
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert "error" in data
        assert "timestamp" in data
        assert "Database connection failed" in data["error"]
    
    def test_health_check_with_partial_failure(self):
        """Test health check handles partial system failures."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Even if some systems fail, health check should still work
        assert data["status"] == "healthy"
        assert data["checks"]["database"] in ["healthy", "checking", "error"]
    
    def test_detailed_health_check_with_mock_exception(self, mock_db):
        """Test detailed health check handles exceptions."""
        # Mock database to raise an exception
        mock_db.__aenter__.side_effect = Exception("System error")
        
        response = client.get("/api/health/detailed")
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert "error" in data
        assert "System error" in data["error"]
    
    def test_health_check_response_headers(self):
        """Test that health check endpoints include appropriate headers."""
        response = client.get("/api/health")
        
        # Check that content type is JSON
        assert response.headers["content-type"] == "application/json"
        
        # Check that cache control is set
        assert "cache-control" in response.headers
        
        # Check that CORS headers are present
        assert "access-control-allow-origin" in response.headers
    
    def test_health_check_timing(self):
        """Test that health check endpoints respond quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/api/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_health_check_consistency(self):
        """Test that health check endpoints return consistent data."""
        # Make multiple requests
        responses = [client.get("/api/health") for _ in range(3)]
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
        
        # All responses should have the same structure
        first_data = responses[0].json()
        for response in responses[1:]:
            data = response.json()
            assert set(data.keys()) == set(first_data.keys())
    
    def test_health_check_with_different_methods(self):
        """Test that health check endpoints work with different HTTP methods."""
        # Test GET method
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # Test POST method (should fail)
        response = client.post("/api/health")
        assert response.status_code == 405
        
        # Test PUT method (should fail)
        response = client.put("/api/health")
        assert response.status_code == 405
        
        # Test DELETE method (should fail)
        response = client.delete("/api/health")
        assert response.status_code == 405
    
    def test_health_check_authentication_not_required(self):
        """Test that health check endpoints don't require authentication."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "TaskManager"
    
    def test_health_check_with_mock_performance_data(self, mock_db):
        """Test health check with performance data."""
        # Mock database to return performance data
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.fetchone.return_value = [50.5]
        
        response = client.get("/api/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include system performance metrics
        assert "system" in data
        assert "cpu_percent" in data["system"]
        assert "memory_rss" in data["system"]