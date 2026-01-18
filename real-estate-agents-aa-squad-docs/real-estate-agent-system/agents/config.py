"""
Configuration settings for the AG2 Multi-Agent System
"""

import os

class Settings:
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/real_estate_agents")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # AI Services
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    portkey_api_key: str = os.getenv("PORTKEY_API_KEY", "")
    portkey_virtual_key: str = os.getenv("PORTKEY_VIRTUAL_KEY", "")
    
    # Application Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

# Global settings instance
settings = Settings()