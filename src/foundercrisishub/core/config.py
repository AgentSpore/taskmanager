from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./test.db"
    cors_origins: str = "*"
    log_level: str = "INFO"
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
