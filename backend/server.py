"""FastAPI Server - Riesgo IA Backend (Refactorizado)

Sistema de Matriz de Riesgos SST con arquitectura mejorada
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import structlog

from core.config import settings
from api.v1 import sst_api
from api.middleware.security import (
    limiter,
    SecurityHeadersMiddleware,
    FileSizeValidationMiddleware,
    rate_limit_exceeded_handler
)
from slowapi.errors import RateLimitExceeded
from shared.exceptions import RiesgoIAException

# Configurar structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info(
        "server_starting",
        app=settings.APP_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT
    )
    logger.info("features", 
        metodologias=["GTC 45", "RAM"],
        llm=f"{settings.LLM_MODEL_PROVIDER}/{settings.LLM_MODEL_NAME}",
        database="MongoDB"
    )
    
    yield
    
    # Shutdown
    from db.mongodb import mongodb
    mongodb.close()
    logger.info("server_stopped")

# Crear app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Sistema inteligente de Matriz de Riesgos SST (GTC 45 + RAM)",
    docs_url="/api/docs" if settings.DEBUG else None,  # Ocultar en prod
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Security Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(FileSizeValidationMiddleware)

# CORS con lista blanca
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)

# Exception handlers
@app.exception_handler(RiesgoIAException)
async def riesgo_ia_exception_handler(request: Request, exc: RiesgoIAException):
    """Handler para excepciones custom"""
    logger.error(
        "custom_exception",
        exception=exc.__class__.__name__,
        message=exc.message,
        detail=exc.detail,
        path=request.url.path
    )
    
    status_code = 400
    if isinstance(exc, RiesgoIAException):
        from shared.exceptions import (
            ValidationError, FileTooLargeError, UnsupportedFileTypeError,
            MatrizNotFoundError
        )
        
        if isinstance(exc, (ValidationError, FileTooLargeError, UnsupportedFileTypeError)):
            status_code = 400
        elif isinstance(exc, MatrizNotFoundError):
            status_code = 404
        else:
            status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler para excepciones no manejadas"""
    logger.critical(
        "unhandled_exception",
        exception=str(exc),
        path=request.url.path,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


# Incluir routers
app.include_router(sst_api.router, prefix="/api/v1", tags=["Matriz SST"])


@app.get("/")
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "descripcion": "Sistema de Matriz de Riesgos SST",
        "metodologias": [
            "GTC 45 - Guía Técnica Colombiana",
            "RAM - Risk Assessment Matrix"
        ],
        "features": {
            "extraccion_automatica_empresa": True,
            "formatos_soportados": ["PDF", "Word", "Excel"],
            "rate_limiting": f"{settings.RATE_LIMIT_PER_MINUTE} requests/min",
            "max_file_size": f"{settings.MAX_FILE_SIZE_MB}MB"
        },
        "llm": f"{settings.LLM_MODEL_PROVIDER}/{settings.LLM_MODEL_NAME}"
    }


@app.get("/api/health")
async def health_check():
    """Health check con validación de dependencias"""
    from db.mongodb import mongodb
    
    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
    
    # Check MongoDB
    try:
        mongodb.db.command('ping')
        health_status["database"] = "connected"
    except Exception as e:
        logger.error("mongodb_health_check_failed", error=str(e))
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check LLM config
    health_status["llm"] = {
        "provider": settings.LLM_MODEL_PROVIDER,
        "model": settings.LLM_MODEL_NAME,
        "configured": bool(settings.EMERGENT_LLM_KEY)
    }
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health_status)
