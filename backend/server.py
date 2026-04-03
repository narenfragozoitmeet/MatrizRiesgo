"""FastAPI Server - Riesgo IA Backend

API REST para sistema multi-agente de matrices de riesgos GTC 45 y RAM
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1 import ingest, matrix, sources
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Sistema multi-agente para generación automática de matrices de riesgos SST",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(ingest.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(matrix.router, prefix="/api/v1", tags=["Matrix"])
app.include_router(sources.router, prefix="/api/v1", tags=["Sources"])

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "arquitectura": "Multi-Agente LangGraph + Medallón (Bronze/Silver/Gold)"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} v{settings.VERSION} iniciado")
    logger.info("Arquitectura: Multi-Agente con LangGraph")
    logger.info("Base de datos: PostgreSQL (Bronze/Silver/Gold)")
    logger.info("Cola de tareas: Celery + Redis")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Apagando servidor...")