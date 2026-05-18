"""
Category schemas for TaskManager.

Pydantic models for category data validation and serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: str = Field("#007bff", description="Category color (hex code)")


class CategoryCreate(CategoryBase):
    """Schema for creating new categories."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating existing categories."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: Optional[str] = Field(None, description="Category color (hex code)")
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must be a hex code starting with #')
        if v and len(v) != 7:
            raise ValueError('Color must be a valid hex code (e.g., #RRGGBB)')
        return v


class CategoryRead(CategoryBase):
    """Schema for reading category data (includes database fields)."""
    id: int
    created_at: datetime
    updated_at: datetime
    task_count: int = Field(0, description="Number of tasks in this category")
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Response schema for category list."""
    categories: List[CategoryRead]
    total: int


class CategoryAnalytics(BaseModel):
    """Analytics data for categories."""
    total_categories: int
    total_tasks: int
    average_tasks_per_category: float
    categories_by_task_count: List[Dict[str, Any]]
    most_active_category: Optional[CategoryRead] = None
    least_active_category: Optional[CategoryRead] = None


class CategoryBulkUpdate(BaseModel):
    """Schema for bulk category operations."""
    category_ids: List[int] = Field(..., min_items=1, description="List of category IDs")
    color: Optional[str] = Field(None, description="New color")


class CategoryImportRequest(BaseModel):
    """Request for category import."""
    data: List[CategoryCreate] = Field(..., description="List of categories to import")


class CategoryExportRequest(BaseModel):
    """Request for category export."""
    format: str = Field(..., regex="^(csv|json)$", description="Export format")
    include_task_count: bool = Field(True, description="Include task counts")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")