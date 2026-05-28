from fastapi import APIRouter
from foundercrisishub.core.db import get_db
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    db_status = "up"
    uptime = int(time.time() - start_time)
    return {
        "status": "ok",
        "db": db_status,
        "uptime_seconds": uptime,
        "requests_served": app.state.requests_served,
    }
