"""
Task management API endpoints for TaskManager.

Provides CRUD operations for tasks, including AI-powered features.
"""

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from loguru import logger

from ..core.database import get_db
from ..schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskListResponse,
    TaskAnalyticsResponse,
)
from ..services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    task: TaskCreate,
    db=Depends(get_db)
) -> TaskRead:
    """
    Create a new task with AI-powered suggestions.
    """
    try:
        logger.info(f"Creating task: {task.title}")
        
        task_service = TaskService(db)
        created_task = await task_service.create_task(task)
        
        logger.info(f"Task created successfully: {created_task.id}")
        return created_task
        
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of tasks to return"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    db=Depends(get_db)
) -> TaskListResponse:
    """
    List tasks with filtering and pagination.
    """
    try:
        logger.info(f"Listing tasks: skip={skip}, limit={limit}, priority={priority}")
        
        task_service = TaskService(db)
        tasks, total = await task_service.list_tasks(
            skip=skip,
            limit=limit,
            priority=priority,
            status=status,
            category_id=category_id,
        )
        
        return TaskListResponse(
            tasks=tasks,
            total=total,
            skip=skip,
            limit=limit,
            has_more=total > skip + limit,
        )
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    db=Depends(get_db)
) -> TaskRead:
    """
    Get a specific task by ID.
    """
    try:
        logger.info(f"Getting task: {task_id}")
        
        task_service = TaskService(db)
        task = await task_service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db=Depends(get_db)
) -> TaskRead:
    """
    Update an existing task.
    """
    try:
        logger.info(f"Updating task: {task_id}")
        
        task_service = TaskService(db)
        updated_task = await task_service.update_task(task_id, task_update)
        
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Task updated successfully: {task_id}")
        return updated_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db=Depends(get_db)
) -> JSONResponse:
    """
    Delete a task by ID.
    """
    try:
        logger.info(f"Deleting task: {task_id}")
        
        task_service = TaskService(db)
        deleted = await task_service.delete_task(task_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Task deleted successfully: {task_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Task deleted successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics/overview", response_model=TaskAnalyticsResponse)
async def get_task_analytics(
    db=Depends(get_db)
) -> TaskAnalyticsResponse:
    """
    Get task analytics and insights.
    """
    try:
        logger.info("Getting task analytics")
        
        task_service = TaskService(db)
        analytics = await task_service.get_task_analytics()
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get task analytics: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/prioritize")
async def prioritize_tasks(
    db=Depends(get_db)
) -> JSONResponse:
    """
    AI-powered task prioritization.
    """
    try:
        logger.info("Running AI-powered task prioritization")
        
        task_service = TaskService(db)
        prioritized_count = await task_service.prioritize_tasks()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Task prioritization completed",
                "prioritized_count": prioritized_count,
                "timestamp": time.time(),
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to prioritize tasks: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/suggest")
async def suggest_tasks(
    db=Depends(get_db)
) -> JSONResponse:
    """
    AI-powered task suggestions based on patterns.
    """
    try:
        logger.info("Generating AI-powered task suggestions")
        
        task_service = TaskService(db)
        suggestions = await task_service.suggest_tasks()
        
        return JSONResponse(
            status_code=200,
            content={
                "suggestions": suggestions,
                "timestamp": time.time(),
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate task suggestions: {e}")
        raise HTTPException(status_code=400, detail=str(e))