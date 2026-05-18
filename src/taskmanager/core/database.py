"""
Database connection and models for TaskManager.

Handles database initialization, connection, and model definitions.
"""

import aiosqlite
import time
from typing import AsyncGenerator, Dict, Any, Optional
from loguru import logger
from contextlib import asynccontextmanager

from .config import settings


class Database:
    """
    Database connection manager with connection pooling.
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection_pool = []
        self.max_pool_size = settings.database_pool_size
        self.max_overflow = settings.database_max_overflow
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """
        Get a database connection from the pool or create a new one.
        """
        start_time = time.time()
        
        try:
            # Try to get a connection from the pool
            if self.connection_pool:
                connection = self.connection_pool.pop()
            else:
                connection = await aiosqlite.connect(self.database_url)
                connection.row_factory = aiosqlite.Row
            
            yield connection
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            # Return connection to pool or close
            if len(self.connection_pool) < self.max_pool_size:
                self.connection_pool.append(connection)
            else:
                await connection.close()
            
            logger.debug(f"Database operation completed in {time.time() - start_time:.3f}s")


# Global database instance
db_instance = Database(settings.database_url)


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Dependency function for FastAPI to get database connection.
    """
    async with db_instance.get_connection() as connection:
        yield connection


async def init_db() -> None:
    """
    Initialize the database with tables and relationships.
    """
    try:
        logger.info("Initializing database...")
        
        async with db_instance.get_connection() as connection:
            # Enable foreign key constraints
            await connection.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    color TEXT DEFAULT '#007bff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    category_id INTEGER,
                    due_date TIMESTAMP,
                    estimated_hours INTEGER,
                    actual_hours INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    depends_on_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    UNIQUE(task_id, depends_on_id)
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    full_name TEXT,
                    hashed_password TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    owner_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(team_id, user_id)
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS task_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(task_id, user_id)
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS task_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed_at)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_tags_task ON task_tags(task_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_task ON task_dependencies(task_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_depends ON task_dependencies(depends_on_id)")
            
            # Create triggers for updated_at timestamps
            await connection.execute("""
                CREATE TRIGGER IF NOT EXISTS update_tasks_updated_at
                AFTER UPDATE ON tasks
                FOR EACH ROW
                BEGIN
                    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
            
            await connection.execute("""
                CREATE TRIGGER IF NOT EXISTS update_categories_updated_at
                AFTER UPDATE ON categories
                FOR EACH ROW
                BEGIN
                    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
            
            await connection.execute("""
                CREATE TRIGGER IF NOT EXISTS update_users_updated_at
                AFTER UPDATE ON users
                FOR EACH ROW
                BEGIN
                    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
            
            await connection.execute("""
                CREATE TRIGGER IF NOT EXISTS update_teams_updated_at
                AFTER UPDATE ON teams
                FOR EACH ROW
                BEGIN
                    UPDATE teams SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
            
            await connection.execute("""
                CREATE TRIGGER IF NOT EXISTS update_comments_updated_at
                AFTER UPDATE ON task_comments
                FOR EACH ROW
                BEGIN
                    UPDATE task_comments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
            
            # Commit changes
            await connection.commit()
            
            logger.info("Database initialized successfully")
            
            # Insert sample data if database is empty
            await insert_sample_data(connection)
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def insert_sample_data(connection: aiosqlite.Connection) -> None:
    """
    Insert sample data for development.
    """
    try:
        # Check if categories exist
        cursor = await connection.execute("SELECT COUNT(*) FROM categories")
        count = await cursor.fetchone()
        
        if count[0] == 0:
            # Insert sample categories
            sample_categories = [
                ("Work", "Work-related tasks", "#007bff"),
                ("Personal", "Personal tasks and projects", "#28a745"),
                ("Urgent", "Urgent tasks", "#dc3545"),
                ("Learning", "Learning and development", "#ffc107"),
            ]
            
            await connection.executemany(
                "INSERT INTO categories (name, description, color) VALUES (?, ?, ?)",
                sample_categories
            )
            
            logger.info("Sample categories inserted")
        
        # Check if users exist
        cursor = await connection.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        
        if count[0] == 0:
            # Insert sample users
            await connection.execute("""
                INSERT INTO users (username, email, full_name, hashed_password, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "admin", "admin@example.com", "Administrator", 
                "hashed_password_placeholder", True
            ))
            
            logger.info("Sample users inserted")
        
        await connection.commit()
        
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")
        await connection.rollback()


async def get_db_stats() -> Dict[str, Any]:
    """
    Get database statistics.
    """
    try:
        async with db_instance.get_connection() as connection:
            stats = {}
            
            # Table counts
            cursor = await connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = await cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor = await connection.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = await cursor.fetchone()
                stats[table_name] = count[0]
            
            # Database size
            cursor = await connection.execute("PRAGMA page_count")
            page_count = await cursor.fetchone()
            cursor = await connection.execute("PRAGMA page_size")
            page_size = await cursor.fetchone()
            
            stats["database_size_bytes"] = page_count[0] * page_size[0]
            stats["database_size_mb"] = stats["database_size_bytes"] / (1024 * 1024)
            
            return stats
            
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {}