from foundercrisishub.schemas.crisis import CrisisCreate, CrisisRead, CrisisList
from foundercrisishub.core.db import get_db

class CrisisService:
    async def create_crisis(self, data: CrisisCreate) -> CrisisRead:
        async with get_db() as db:
            cursor = await db.execute(
                "INSERT INTO crises (title, description) VALUES (?, ?)",
                (data.title, data.description),
            )
            await db.commit()
            crisis_id = cursor.lastrowid
            return await self.get_crisis(crisis_id)

    async def list_crises(self) -> CrisisList:
        async with get_db() as db:
            rows = await db.execute_fetchall("SELECT * FROM crises")
            items = [CrisisRead(**dict(row)) for row in rows]
            return CrisisList(items=items)

    async def get_crisis(self, crisis_id: int) -> CrisisRead | None:
        async with get_db() as db:
            row = await db.execute_fetchone("SELECT * FROM crises WHERE id = ?", (crisis_id,))
            if row:
                return CrisisRead(**dict(row))
            return None

    async def add_comment(self, crisis_id: int, comment: str) -> None:
        async with get_db() as db:
            await db.execute(
                "INSERT INTO comments (crisis_id, comment) VALUES (?, ?)",
                (crisis_id, comment),
            )
            await db.commit()
