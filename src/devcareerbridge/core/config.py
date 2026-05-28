from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./devcareerbridge.db"
    cors_origins: str = "*"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def settings():
    return Settings()
