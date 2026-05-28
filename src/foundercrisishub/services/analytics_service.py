from foundercrisishub.core.db import get_db

async def get_analytics():
    db = await get_db()
    row = await db.execute_fetchone("SELECT COUNT(*) as total FROM crises")
    return {"total_crises": row["total"] if row else 0}
