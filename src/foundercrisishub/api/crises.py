from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from foundercrisishub.services.crises_service import create_crisis, list_crises, get_crisis

router = APIRouter()

class CrisisCreate(BaseModel):
    title: str
    description: str
    severity: str

class CrisisRead(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    created_at: str

@router.post("/crises", response_model=CrisisRead)
async def create(crisis: CrisisCreate):
    return await create_crisis(crisis)

@router.get("/crises", response_model=list[CrisisRead])
async def list_all():
    return await list_crises()

@router.get("/crises/{crisis_id}", response_model=CrisisRead)
async def read(crisis_id: int):
    result = await get_crisis(crisis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Crisis not found")
    return result
