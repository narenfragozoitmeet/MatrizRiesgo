"""Configuración centralizada usando Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Riesgo IA"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://riesgo_admin:riesgo_secure_2024@localhost:5432/riesgo_ia"
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # AI/LLM
    EMERGENT_LLM_KEY: str
    LLM_MODEL_PROVIDER: str = "gemini"
    LLM_MODEL_NAME: str = "gemini-2.5-flash"
    
    # Storage
    STORAGE_URL: str = "https://integrations.emergentagent.com/objstore/api/v1/storage"
    
    # Sources Pipeline
    SOURCES_CONFIG_PATH: str = "./sources_config.yaml"
    SOURCES_UPDATE_ENABLED: bool = True
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()