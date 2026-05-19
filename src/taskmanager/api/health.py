"""
Health check API endpoint for TaskManager.

Provides health status and monitoring information for the application.
"""

import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Dict, Any

from ..core import settings

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check(request: Request) -> Dict[str, Any]:
    """
    Health check endpoint for monitoring application status.
    
    Returns comprehensive health status including:
    - Application status
    - Database connectivity
    - Uptime information
    - Request metrics
    """
    try:
        # Calculate uptime
        uptime_seconds = time.time() - getattr(request.app.state, 'start_time', time.time())
        
        # Check database health (placeholder - will be implemented later)
        db_status = "healthy"  # TODO: Implement actual database health check
        
        # Prepare health response
        health_data = {
            "status": "healthy",
            "service": "TaskManager",
            "version": "0.1.0",
            "environment": settings.environment,
            "database": db_status,
            "uptime_seconds": uptime_seconds,
            "requests_served": getattr(request.app.state, 'requests_served', 0),
            "timestamp": time.time(),
            "checks": {
                "database": db_status,
                "cors": "enabled",
                "logging": "enabled",
            }
        }
        
        logger.info(f"Health check passed: {health_data}")
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "TaskManager",
                "version": "0.1.0",
                "error": str(e),
                "timestamp": time.time(),
            },
        )


@router.get("/health/detailed")
async def detailed_health_check(request: Request) -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Returns extended health information including system metrics.
    """
    import psutil
    import os
    
    try:
        # System information
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        health_data = {
            "status": "healthy",
            "service": "TaskManager",
            "version": "0.1.0",
            "environment": settings.environment,
            "system": {
                "cpu_percent": process.cpu_percent(),
                "memory_rss": memory_info.rss,
                "memory_vms": memory_info.vms,
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "num_handles": process.num_handles(),
            },
            "uptime_seconds": time.time() - getattr(request.app.state, 'start_time', time.time()),
            "requests_served": getattr(request.app.state, 'requests_served', 0),
            "timestamp": time.time(),
            "python_version": os.sys.version,
            "platform": os.sys.platform,
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
            },
        )


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint for basic connectivity testing.
    """
    return {"message": "pong", "timestamp": time.time()}