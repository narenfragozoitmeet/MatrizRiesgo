"""Configuración centralizada usando Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Riesgo IA"
    VERSION: str = "1.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database - MongoDB
    MONGO_URL: str  # Sin default - debe venir de .env
    DB_NAME: str = "riesgo_ia"
    
    # Database - PostgreSQL (opcional, para arquitectura híbrida)
    POSTGRES_URL: str | None = None
    
    # AI/LLM
    EMERGENT_LLM_KEY: str  # Sin default - debe venir de .env
    LLM_MODEL_PROVIDER: str = "gemini"
    LLM_MODEL_NAME: str = "gemini-2.5-flash"
    
    # Security - JWT
    JWT_SECRET_KEY: str  # Sin default - debe venir de .env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 horas
    
    # Security - CORS
    CORS_ORIGINS: str  # Sin default - debe venir de .env
    MAX_FILE_SIZE_MB: int = 100
    RATE_LIMIT_PER_MINUTE: int = 5
    
    # Redis (para Celery)
    REDIS_URL: str | None = None
    
    # Celery
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte string de CORS a lista"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convierte MB a bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()