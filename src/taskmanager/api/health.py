from fastapi import APIRouter, Request
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    return {
        "status": "healthy",
        "db": "connected",
        "uptime_seconds": 0,
        "requests_served": getattr(request.app.state, "requests_served", 0)
    }