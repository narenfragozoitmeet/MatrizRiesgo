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
from api.v1 import sst_api, pipeline_api, auth_api
from api.security_middleware import (
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
    
    # Inicializar Pipeline System
    await initialize_pipeline_system()
    
    yield
    
    # Shutdown
    from db.mongodb import mongodb
    mongodb.close()
    
    # Detener Pipeline Scheduler
    if pipeline_api.pipeline_scheduler:
        pipeline_api.pipeline_scheduler.stop()
    
    logger.info("server_stopped")


async def initialize_pipeline_system():
    """Inicializa el sistema de pipelines de ingesta automática"""
    import yaml
    from pathlib import Path
    from services.pipeline import PipelineManager, PipelineScheduler
    from services.pipeline.sources import ExampleDataSource
    
    try:
        # Cargar configuración
        config_path = Path("/app/backend/config/pipeline_config.yaml")
        
        if not config_path.exists():
            logger.warning("pipeline_config_not_found", message="Pipeline config no encontrado, usando defaults")
            return
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config.get('pipeline', {}).get('enabled', False):
            logger.info("pipeline_disabled", message="Sistema de pipeline deshabilitado en configuración")
            return
        
        # Inicializar manager
        manager = PipelineManager()
        
        # Registrar fuentes desde config
        sources_config = config.get('sources', {})
        for source_id, source_conf in sources_config.items():
            if source_conf.get('enabled', False):
                # Por ahora solo soportamos ExampleDataSource
                # Cuando se agreguen fuentes reales, usar source_conf['type'] para instanciar
                source = ExampleDataSource(source_id, source_conf.get('config', {}))
                manager.register_source(source)
                logger.info("pipeline_source_registered", source_id=source_id)
        
        # Inicializar scheduler
        scheduler = PipelineScheduler(manager)
        
        # Agregar schedules desde config
        for source_id, source_conf in sources_config.items():
            if source_conf.get('enabled', False) and 'schedule' in source_conf:
                scheduler.add_schedule(source_id, source_conf['schedule'])
                logger.info("pipeline_schedule_added", 
                           source_id=source_id, 
                           cron=source_conf['schedule'])
        
        # Iniciar scheduler
        scheduler.start()
        
        # Hacer disponibles globalmente en pipeline_api
        pipeline_api.pipeline_manager = manager
        pipeline_api.pipeline_scheduler = scheduler
        
        logger.info("pipeline_system_initialized", 
                   sources=len(manager.sources),
                   schedules=len(scheduler.get_schedules()))
        
    except Exception as e:
        logger.error("pipeline_initialization_failed", error=str(e), exc_info=True)

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

# CORS con validación mejorada
cors_origins = settings.cors_origins_list

# Validar CORS en producción
if settings.ENVIRONMENT == "production":
    if "*" in cors_origins:
        logger.critical("CORS wildcard (*) detectado en PRODUCCIÓN - RIESGO DE SEGURIDAD")
        raise ValueError("CORS_ORIGINS no puede ser '*' en producción")
    
    if settings.cors_origins_list and settings.cors_origins_list[0] == "*" and True:  # allow_credentials
        logger.critical("CORS wildcard con allow_credentials=True - VULNERABILIDAD CRÍTICA")
        raise ValueError("No se puede usar CORS='*' con allow_credentials=True")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
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
        exception_type=exc.__class__.__name__,
        path=request.url.path,
        exc_info=True
    )
    
    # En producción, NO exponer detalles internos
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor. Contacte al administrador.",
                "error_id": f"{request.url.path}_{exc.__class__.__name__}"  # Para tracking
            }
        )
    else:
        # En desarrollo, mostrar detalles para debugging
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor",
                "error": str(exc),
                "type": exc.__class__.__name__,
                "path": request.url.path
            }
        )


# Incluir routers
app.include_router(auth_api.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(sst_api.router, prefix="/api/v1", tags=["Matriz SST"])
app.include_router(pipeline_api.router, prefix="/api/v1", tags=["Pipeline"])


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
