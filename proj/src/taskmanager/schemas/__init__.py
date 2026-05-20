"""
Pydantic schemas for TaskManager.

This package contains all the data models and schemas used
for request/response validation and serialization.
"""

from .task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskListResponse,
    TaskAnalyticsResponse,
)

from .category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryListResponse,
)

from .team import (
    TeamCreate,
    TeamRead,
    TeamUpdate,
    TeamListResponse,
)

__all__ = [
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    "TaskListResponse",
    "TaskAnalyticsResponse",
    "CategoryCreate",
    "CategoryRead",
    "CategoryUpdate",
    "CategoryListResponse",
    "TeamCreate",
    "TeamRead",
    "TeamUpdate",
    "TeamListResponse",
]