"""Base de datos - Configuración y sesión

SQLAlchemy 2.x con soporte para esquemas múltiples (Bronze, Silver, Gold)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Engine con pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa la base de datos (crea tablas)"""
    # Importar todos los modelos aquí para que SQLAlchemy los registre
    from db.schemas import bronze, silver, gold
    
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")