"""FastAPI Server - Riesgo IA Backend

API REST para generación automática de matrices de riesgos SST y Legales
Powered by LLM Agents + Gemini 2.5 Flash
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1 import unified_api
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
    logger.info("📊 Arquitectura: Multi-Agente con LLM (Gemini 2.5 Flash)")
    logger.info("🗄️  Base de datos: MongoDB (Arquitectura Medallón)")
    logger.info("🤖 Agentes: Extractor → Identificador → Evaluador → Generador")
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
    description="Sistema inteligente para generación automática de matrices de riesgos SST (GTC 45) y Riesgos Legales usando IA",
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
app.include_router(unified_api.router, prefix="/api/v1", tags=["Matriz de Riesgos"])

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "tipos_matrices": ["SST (GTC 45)", "Riesgos Legales"],
        "metodologias": ["GTC 45", "RAM (Risk Assessment Matrix)", "Análisis Normativo"],
        "llm": f"{settings.LLM_MODEL_PROVIDER}/{settings.LLM_MODEL_NAME}"
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
            "llm": f"{settings.LLM_MODEL_PROVIDER}/{settings.LLM_MODEL_NAME}"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }