import aiosqlite
from contextlib import asynccontextmanager
from .config import settings

@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(settings().database_url.replace("sqlite:///", "")) as db:
        yield db

async def init_db():
    async with aiosqlite.connect("tasks.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT "pending",
            priority TEXT DEFAULT "medium",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TEXT
        )
        """)
        await db.commit()