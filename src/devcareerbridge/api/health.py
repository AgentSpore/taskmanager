from fastapi import APIRouter
import time
from devcareerbridge.core.db import get_db

router = APIRouter()

@router.get("/health")
async def health():
    db_status = "ok"
    try:
        async with get_db() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        db_status = "error"
    uptime = time.time() - time.process_time()
    requests = getattr(router.app.state, "requests_served", 0) if hasattr(router, "app") else 0
    return {"status": "ok", "db": db_status, "uptime_seconds": uptime, "requests_served": requests}
