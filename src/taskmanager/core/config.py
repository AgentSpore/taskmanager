from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "taskmanager"
    database_url: str = "sqlite:///./tasks.db"
    debug: bool = True
    
    class Config:
        env_file = ".env"

@lru_cache()
def settings() -> Settings:
    return Settings()