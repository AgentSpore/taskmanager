"""
Core application components for TaskManager.

This package contains the core logic including configuration,
database management, and security features.
"""

from .config import settings
from .database import get_db, init_db

__all__ = ["settings", "get_db", "init_db"]