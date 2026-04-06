"""Configuración centralizada usando Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Riesgo IA"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - MongoDB
    MONGO_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "riesgo_ia"
    
    # AI/LLM
    EMERGENT_LLM_KEY: str
    LLM_MODEL_PROVIDER: str = "gemini"
    LLM_MODEL_NAME: str = "gemini-2.5-flash"
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()