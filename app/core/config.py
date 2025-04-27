from typing import Dict, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Webhook Delivery Service"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/webhooks"
    TEST_DATABASE_URL: Optional[str] = None
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    
    # Webhook settings
    MAX_RETRY_ATTEMPTS: int = 5
    RETRY_INTERVALS: Dict[int, int] = {
        1: 10,  # 10 seconds
        2: 30,  # 30 seconds
        3: 60,  # 1 minute
        4: 300,  # 5 minutes
        5: 900,  # 15 minutes
    }
    DELIVERY_TIMEOUT: int = 10  # seconds
    
    # Log retention in hours
    LOG_RETENTION_HOURS: int = 72
    
    SECRET_KEY: str = "your-local-dev-secret-key-change-in-production"
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "127.0.0.1,localhost"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()