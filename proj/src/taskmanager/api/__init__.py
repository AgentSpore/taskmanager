"""
API endpoints for TaskManager.

This package contains all the API endpoints organized by domain.
"""

# Import all API routers
from .health import router as health_router
from .tasks import router as tasks_router

__all__ = ["health_router", "tasks_router"]