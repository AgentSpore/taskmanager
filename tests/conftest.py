"""
Test fixtures and configuration for TaskManager tests.

This module provides shared fixtures and test configuration
used across all test modules.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import aiosqlite
import tempfile
import os
from pathlib import Path

from src.taskmanager.main import app
from src.taskmanager.core.config import Settings
from src.taskmanager.core.database import init_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Create test settings with temporary database."""
    return Settings(
        database_url="sqlite:///./test_tasks.db",
        debug=True
    )


@pytest.fixture
async def test_db():
    """Create a test database with temporary file."""
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()
    
    # Set database URL to temp file
    original_db_url = Settings().database_url
    Settings.database_url = f"sqlite:///{temp_db.name}"
    
    try:
        # Initialize database
        await init_db()
        
        # Yield the database path for tests
        yield temp_db.name
        
    finally:
        # Restore original database URL
        Settings.database_url = original_db_url
        
        # Clean up temp file
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)


@pytest.fixture
async def client(test_db):
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_client(client):
    """Create an authenticated test client."""
    # For now, we'll use the regular client since authentication isn't implemented yet
    yield client


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task for unit testing",
        "priority": "medium",
        "status": "pending",
        "due_date": "2024-12-31",
        "estimated_hours": 2,
        "tags": ["test", "unit"]
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "name": "Test Category",
        "description": "A test category for unit testing",
        "color": "#007bff"
    }


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "name": "Test Team",
        "description": "A test team for unit testing"
    }


@pytest.fixture
def multiple_tasks_data():
    """Multiple sample tasks for testing list operations."""
    return [
        {
            "title": "Task 1",
            "description": "First test task",
            "priority": "high",
            "status": "pending"
        },
        {
            "title": "Task 2", 
            "description": "Second test task",
            "priority": "medium",
            "status": "in_progress"
        },
        {
            "title": "Task 3",
            "description": "Third test task", 
            "priority": "low",
            "status": "completed"
        }
    ]


@pytest.fixture
def task_update_data():
    """Task update data for testing."""
    return {
        "title": "Updated Task Title",
        "description": "Updated task description",
        "priority": "high",
        "status": "in_progress",
        "estimated_hours": 4
    }