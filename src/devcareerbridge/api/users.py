from fastapi import APIRouter, HTTPException, Depends
from devcareerbridge.schemas.user import UserCreate, UserRead
from devcareerbridge.services.user_service import create_user, get_user, list_users

router = APIRouter()

@router.post("/users", response_model=UserRead)
async def create(user: UserCreate):
    return await create_user(user)

@router.get("/users/{user_id}", response_model=UserRead)
async def read(user_id: int):
    usr = await get_user(user_id)
    if not usr:
        raise HTTPException(status_code=404, detail="User not found")
    return usr

@router.get("/users", response_model=list[UserRead])
async def list_all():
    return await list_users()
