# app/core/config.py
from typing import List, Any
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Ecommerce API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI Ecommerce Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ecommerce"

    # Security Settings
    SECRET_KEY: str = "your-super-secret-key-should-be-very-long-and-secure"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()