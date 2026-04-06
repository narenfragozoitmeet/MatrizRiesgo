"""FastAPI Server - Riesgo IA Backend

API REST para generación automática de Matrices de Riesgos SST (GTC 45 + RAM)
Powered by LLM Agents + Gemini 2.5 Flash
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1 import sst_api
import logging
from contextlib import asynccontextmanager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} iniciando...")
    logger.info("📊 Matriz SST - Identificación de Peligros y Valoración de Riesgos")
    logger.info("🔧 Metodologías: GTC 45 (Guía Técnica Colombiana) + RAM (Risk Assessment Matrix)")
    logger.info("🗄️  Base de datos: MongoDB (Arquitectura Medallón)")
    logger.info("🤖 LLM: Gemini 2.5 Flash via emergentintegrations")
    logger.info("✅ Servidor listo!")
    
    yield
    
    # Shutdown
    from db.mongodb import mongodb
    mongodb.close()
    logger.info("👋 Servidor apagado")

# Crear app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Sistema inteligente para generación automática de Matrices de Riesgos SST (Seguridad y Salud en el Trabajo) según GTC 45",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
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
app.include_router(sst_api.router, prefix="/api/v1", tags=["Matriz SST"])

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "descripcion": "Sistema de Matriz de Riesgos SST",
        "metodologias": [
            "GTC 45 - Guía Técnica Colombiana para identificación de peligros y valoración de riesgos",
            "RAM - Risk Assessment Matrix (herramienta externa de cálculo)"
        ],
        "llm": f"{settings.LLM_MODEL_PROVIDER}/{settings.LLM_MODEL_NAME}",
        "extraccion_automatica": "El nombre de la empresa se extrae automáticamente del documento"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    from db.mongodb import mongodb
    try:
        # Test MongoDB connection
        mongodb.db.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "llm": f"{settings.LLM_MODEL_PROVIDER}/{settings.LLM_MODEL_NAME}",
            "tipo_matriz": "Solo SST (Seguridad y Salud en el Trabajo)"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }