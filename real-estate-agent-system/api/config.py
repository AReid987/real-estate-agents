"""
Configuration settings for the API Gateway
"""

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/real_estate_agents")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External services
    ag2_core_url: str = os.getenv("AG2_CORE_URL", "http://localhost:8001")
    langflow_url: str = os.getenv("LANGFLOW_URL", "http://localhost:7860")
    
    # Security
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
    
    # Application settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()