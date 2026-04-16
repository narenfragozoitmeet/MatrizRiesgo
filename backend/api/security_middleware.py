"""Middleware de seguridad y rate limiting"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Rate limiter configurado
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Añade headers de seguridad a todas las respuestas"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class FileSizeValidationMiddleware(BaseHTTPMiddleware):
    """Valida tamaño de archivos en requests multipart"""
    
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
            content_length = request.headers.get("content-length")
            
            if content_length and int(content_length) > settings.max_file_size_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"Archivo muy grande. Máximo {settings.MAX_FILE_SIZE_MB}MB permitido"
                )
        
        return await call_next(request)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler custom para rate limit exceeded"""
    logger.warning(
        f"Rate limit exceeded: {get_remote_address(request)} - {request.url.path}",
        extra={"ip": get_remote_address(request), "path": request.url.path}
    )
    
    return HTTPException(
        status_code=429,
        detail="Demasiadas solicitudes. Por favor intenta más tarde."
    )
