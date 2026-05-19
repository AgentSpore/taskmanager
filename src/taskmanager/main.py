"""
FastAPI application entry point for TaskManager.

This file sets up the main FastAPI application with middleware,
routers, and lifecycle events.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Generator

from .core import settings, init_db
from .api import health_router, tasks_router

# Request counter for monitoring
requests_served = 0
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None, None, None]:
    """
    Application lifespan events for startup and shutdown.
    """
    logger.info("Starting TaskManager application...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    logger.info("Shutting down TaskManager application...")


# Create FastAPI app
app = FastAPI(
    title="TaskManager",
    description="AI-powered task management system",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next) -> Response:
    """
    Add request processing time to response headers.
    """
    global requests_served
    requests_served += 1
    
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Requests-Served"] = str(requests_served)
    
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    Log incoming requests for debugging and monitoring.
    """
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {response.status_code}")
    return response


# Include API routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request.headers.get("X-Request-ID"),
        },
    )


@app.get("/")
async def root() -> dict:
    """
    Root endpoint with basic application info.
    """
    uptime_seconds = time.time() - start_time
    
    return {
        "message": "Welcome to TaskManager",
        "version": "0.1.0",
        "docs_url": "/docs",
        "uptime_seconds": uptime_seconds,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "taskmanager.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )