"""Configuración centralizada usando Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # === APP ===
    APP_NAME: str = "Matriz Riesgos SST"
    VERSION: str = "1.2.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # === DATABASE ===
    MONGO_URL: str  # Requerido desde .env
    DB_NAME: str = "riesgo_ia"
    
    # === AI/LLM ===
    EMERGENT_LLM_KEY: str  # Requerido desde .env
    LLM_MODEL_PROVIDER: str = "gemini"
    LLM_MODEL_NAME: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 8000
    
    # === SECURITY - JWT ===
    JWT_SECRET_KEY: str  # Requerido desde .env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 horas
    
    # === SECURITY - CORS & FILES ===
    CORS_ORIGINS: str  # Requerido desde .env
    MAX_FILE_SIZE_MB: int = 100
    RATE_LIMIT_PER_MINUTE: int = 5
    
    # === PIPELINE ===
    PIPELINE_ENABLED: bool = False
    PIPELINE_AUTO_PROCESS: bool = True
    PIPELINE_STORAGE_PATH: str = "/app/data/pipeline_ingestion"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de orígenes CORS"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Retorna tamaño máximo de archivo en bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
