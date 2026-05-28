from foundercrisishub.core.db import get_db
from foundercrisishub.api.crises import CrisisCreate, CrisisRead

async def create_crisis(crisis: CrisisCreate) -> CrisisRead:
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO crises (title, description, severity) VALUES (?, ?, ?)",
        (crisis.title, crisis.description, crisis.severity)
    )
    await db.commit()
    crisis_id = cursor.lastrowid
    return await get_crisis(crisis_id)

async def list_crises():
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM crises")
    return [CrisisRead(**dict(row)) for row in rows]

async def get_crisis(crisis_id: int):
    db = await get_db()
    row = await db.execute_fetchone("SELECT * FROM crises WHERE id = ?", (crisis_id,))
    if row:
        return CrisisRead(**dict(row))
    return None
