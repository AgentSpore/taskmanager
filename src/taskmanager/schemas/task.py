"""
Task schemas for TaskManager.

Pydantic models for task data validation and serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    """Task status levels."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")
    status: Status = Field(Status.PENDING, description="Task status")
    category_id: Optional[int] = Field(None, description="Category ID")
    due_date: Optional[date] = Field(None, description="Due date")
    estimated_hours: Optional[int] = Field(None, ge=0, le=1000, description="Estimated hours")
    actual_hours: Optional[int] = Field(None, ge=0, le=1000, description="Actual hours")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    depends_on: List[int] = Field(default_factory=list, description="Task dependencies")


class TaskCreate(TaskBase):
    """Schema for creating new tasks."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating existing tasks."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    priority: Optional[Priority] = Field(None, description="Task priority")
    status: Optional[Status] = Field(None, description="Task status")
    category_id: Optional[int] = Field(None, description="Category ID")
    due_date: Optional[date] = Field(None, description="Due date")
    estimated_hours: Optional[int] = Field(None, ge=0, le=1000, description="Estimated hours")
    actual_hours: Optional[int] = Field(None, ge=0, le=1000, description="Actual hours")
    tags: Optional[List[str]] = Field(None, description="Task tags")
    depends_on: Optional[List[int]] = Field(None, description="Task dependencies")
    
    @validator('tags', pre=True)
    def validate_tags(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',')]
        return v or []


class TaskRead(TaskBase):
    """Schema for reading task data (includes database fields)."""
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response schema for task list with pagination."""
    tasks: List[TaskRead]
    total: int
    skip: int
    limit: int
    has_more: bool


class TaskAnalytics(BaseModel):
    """Analytics data for tasks."""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    completed_percentage: float
    average_completion_time: float  # in days
    tasks_by_priority: Dict[str, int]
    tasks_by_status: Dict[str, int]
    tasks_by_category: Dict[str, int]
    productivity_trend: List[Dict[str, Any]]  # daily/weekly productivity data


class TaskAnalyticsResponse(BaseModel):
    """Response schema for task analytics."""
    overview: TaskAnalytics
    top_priority_tasks: List[TaskRead]
    recent_completed_tasks: List[TaskRead]
    upcoming_due_tasks: List[TaskRead]
    productivity_score: float
    recommendations: List[str]


class TaskSuggestion(BaseModel):
    """AI-powered task suggestion."""
    title: str
    description: Optional[str] = None
    priority: Priority
    category_id: Optional[int] = None
    estimated_hours: Optional[int] = None
    confidence_score: float  # 0.0 to 1.0
    reasoning: Optional[str] = None


class TaskPriorityRequest(BaseModel):
    """Request for AI-powered task prioritization."""
    task_ids: List[int] = Field(default_factory=list, description="Task IDs to prioritize (empty for all)")


class TaskSuggestionRequest(BaseModel):
    """Request for AI-powered task suggestions."""
    context: Optional[str] = Field(None, description="Context for suggestions")
    category_id: Optional[int] = Field(None, description="Filter by category")
    priority: Optional[Priority] = Field(None, description="Filter by priority")
    count: int = Field(5, ge=1, le=20, description="Number of suggestions")


class TaskComment(BaseModel):
    """Task comment schema."""
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskCommentCreate(BaseModel):
    """Schema for creating task comments."""
    content: str = Field(..., min_length=1, max_length=1000, description="Comment content")


class TaskAssignment(BaseModel):
    """Task assignment schema."""
    id: int
    task_id: int
    user_id: int
    assigned_at: datetime
    
    class Config:
        from_attributes = True


class TaskDependency(BaseModel):
    """Task dependency schema."""
    id: int
    task_id: int
    depends_on_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskBulkUpdate(BaseModel):
    """Schema for bulk task operations."""
    task_ids: List[int] = Field(..., min_items=1, description="List of task IDs")
    status: Optional[Status] = Field(None, description="New status")
    priority: Optional[Priority] = Field(None, description="New priority")
    category_id: Optional[int] = Field(None, description="New category ID")
    assign_to: Optional[int] = Field(None, description="Assign to user ID")


class TaskExportRequest(BaseModel):
    """Request for task export."""
    format: str = Field(..., regex="^(csv|json|pdf)$", description="Export format")
    task_ids: Optional[List[int]] = Field(None, description="Specific task IDs (empty for all)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    include_completed: bool = Field(True, description="Include completed tasks")


class TaskImportRequest(BaseModel):
    """Request for task import."""
    format: str = Field(..., regex="^(csv|json)$", description="Import format")
    data: str = Field(..., description="Import data")
    category_mapping: Optional[Dict[str, int]] = Field(None, description="Category mapping")
    default_priority: Priority = Field(Priority.MEDIUM, description="Default priority")
    default_status: Status = Field(Status.PENDING, description="Default status")