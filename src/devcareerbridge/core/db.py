import aiosqlite
from contextlib import asynccontextmanager
from .config import settings

@asynccontextmanager
async def get_db():
    db = await aiosqlite.connect(settings().database_url.split('///')[-1])
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    async with get_db() as conn:
        await conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        await conn.commit()
