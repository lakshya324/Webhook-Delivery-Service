from typing import Dict, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Webhook Delivery Service"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/webhooks"
    TEST_DATABASE_URL: Optional[str] = None

    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None

    MAX_RETRY_ATTEMPTS: int = 5
    RETRY_INTERVALS: Dict[int, int] = {
        1: 10,
        2: 30,
        3: 60,
        4: 300,
        5: 900,
    }
    DELIVERY_TIMEOUT: int = 10

    LOG_RETENTION_HOURS: int = 72

    SECRET_KEY: str = "your-local-dev-secret-key-change-in-production"
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "127.0.0.1,localhost"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()