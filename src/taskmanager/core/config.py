"""
Application configuration for TaskManager.

Handles environment variables and application settings.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Basic application info
    app_name: str = "TaskManager"
    app_version: str = "0.1.0"
    app_description: str = "AI-powered task management system"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./taskmanager.db")
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    
    # CORS configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Logging configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE")
    
    # AI/ML configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    ai_enabled: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    
    # Security configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate limiting
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Task management defaults
    default_priority: str = "medium"
    default_status: str = "pending"
    default_due_days: int = int(os.getenv("DEFAULT_DUE_DAYS", "7"))
    
    # Analytics configuration
    analytics_enabled: bool = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
    analytics_retention_days: int = int(os.getenv("ANALYTICS_RETENTION_DAYS", "365"))
    
    # Email configuration
    email_enabled: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    email_from: Optional[str] = os.getenv("EMAIL_FROM")
    
    # Task AI configuration
    task_ai_enabled: bool = os.getenv("TASK_AI_ENABLED", "true").lower() == "true"
    task_ai_suggestions_count: int = int(os.getenv("TASK_AI_SUGGESTIONS_COUNT", "5"))
    task_ai_max_length: int = int(os.getenv("TASK_AI_MAX_LENGTH", "1000"))
    
    # File upload configuration
    file_upload_enabled: bool = os.getenv("FILE_UPLOAD_ENABLED", "false").lower() == "true"
    file_upload_max_size: int = int(os.getenv("FILE_UPLOAD_MAX_SIZE", "10485760"))  # 10MB
    file_upload_allowed_types: List[str] = os.getenv("FILE_UPLOAD_ALLOWED_TYPES", "pdf,jpg,jpeg,png,txt").split(",")
    
    # Development-specific settings
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v
    
    @validator("log_level", pre=True)
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("Database URL is required")
        return v
    
    @validator("cors_origins", pre=True)
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()