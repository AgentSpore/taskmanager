from devcareerbridge.core.db import get_db
from devcareerbridge.schemas.user import UserCreate, UserRead

async def create_user(user: UserCreate) -> UserRead:
    async with get_db() as conn:
        cursor = await conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email)
        )
        await conn.commit()
        user_id = cursor.lastrowid
        return UserRead(id=user_id, name=user.name, email=user.email)

async def get_user(user_id: int):
    async with get_db() as conn:
        cursor = await conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return UserRead(id=row[0], name=row[1], email=row[2])
        return None

async def list_users():
    async with get_db() as conn:
        cursor = await conn.execute("SELECT id, name, email FROM users")
        rows = await cursor.fetchall()
        return [UserRead(id=r[0], name=r[1], email=r[2]) for r in rows]
