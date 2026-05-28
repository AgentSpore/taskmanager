from fastapi import APIRouter
from foundercrisishub.services.analytics_service import get_analytics

router = APIRouter()

@router.get("/analytics")
async def analytics():
    return await get_analytics()
