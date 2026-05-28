import aiosqlite
from foundercrisishub.core.config import get_settings

DB = None

async def get_db():
    global DB
    if DB is None:
        DB = await aiosqlite.connect(get_settings().database_url)
        DB.row_factory = aiosqlite.Row
    return DB

async def init_db():
    db = await get_db()
    await db.executescript('''
    CREATE TABLE IF NOT EXISTS crises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    await db.commit()
