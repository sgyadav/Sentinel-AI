"""Application configuration management"""

import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


def normalize_database_url(database_url: str) -> str:
    """Accept the legacy Render `postgres://` scheme and normalize it for SQLAlchemy."""
    if database_url.startswith("postgres://"):
        return "postgresql://" + database_url.removeprefix("postgres://")
    return database_url


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "SENTINEL AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - Use local path on Windows
    DATABASE_URL: str = normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///./sentinel.db")
    )
    
    # JWT Configuration
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    REQUIRE_HTTPS: bool = False
    PASSWORD_MIN_LENGTH: int = 8
    
    # Real-time Processing
    REALTIME_ENABLED: bool = True
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Telemetry
    HEARTBEAT_TIMEOUT: int = 120  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_database_url_setting(cls, value: str) -> str:
        return normalize_database_url(value)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
