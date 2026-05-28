from pydantic import BaseModel
from datetime import datetime

class CrisisCreate(BaseModel):
    title: str
    description: str | None = None

class CrisisRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    created_at: datetime

class CrisisList(BaseModel):
    items: list[CrisisRead]
