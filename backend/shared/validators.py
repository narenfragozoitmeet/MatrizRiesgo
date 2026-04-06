"""Validadores de documentos y datos"""

from typing import Tuple
from shared.exceptions import FileTooLargeError, UnsupportedFileTypeError, ValidationError
from core.config import settings
import logging
import re

logger = logging.getLogger(__name__)


class DocumentValidator:
    """Validador de documentos subidos"""
    
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    }
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.xlsx', '.xls'}
    
    @classmethod
    def validate_file(cls, filename: str, content_type: str, file_size: int) -> None:
        """
        Valida archivo subido
        
        Args:
            filename: Nombre del archivo
            content_type: MIME type
            file_size: Tamaño en bytes
            
        Raises:
            FileTooLargeError: Si excede tamaño máximo
            UnsupportedFileTypeError: Si tipo no soportado
        """
        # Validar tamaño
        if file_size > settings.max_file_size_bytes:
            raise FileTooLargeError(
                f"Archivo muy grande ({file_size / 1024 / 1024:.1f}MB). Máximo {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Validar MIME type
        if content_type not in cls.ALLOWED_MIME_TYPES:
            raise UnsupportedFileTypeError(
                f"Tipo de archivo no soportado: {content_type}. "
                f"Use PDF, Word (.docx) o Excel (.xlsx)"
            )
        
        # Validar extensión
        ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Extensión no permitida: {ext}"
            )
        
        logger.info(f"✅ Archivo validado: {filename} ({file_size} bytes)")


class TextValidator:
    """Validador de texto extraído"""
    
    MIN_TEXT_LENGTH = 100
    MAX_TEXT_LENGTH = 500000  # 500KB
    
    # Patrones sospechosos (prompt injection)
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"system\s*:",
        r"<script>",
        r"javascript:",
        r"eval\s*\(",
        r"__import__",
    ]
    
    @classmethod
    def validate_text(cls, text: str) -> str:
        """
        Valida y sanitiza texto extraído
        
        Args:
            text: Texto a validar
            
        Returns:
            Texto sanitizado
            
        Raises:
            ValidationError: Si texto inválido
        """
        if not text or len(text.strip()) < cls.MIN_TEXT_LENGTH:
            raise ValidationError(
                f"El documento no contiene suficiente texto. "
                f"Mínimo {cls.MIN_TEXT_LENGTH} caracteres requeridos."
            )
        
        if len(text) > cls.MAX_TEXT_LENGTH:
            logger.warning(f"Texto muy largo ({len(text)} chars), truncando...")
            text = text[:cls.MAX_TEXT_LENGTH]
        
        # Detectar patrones sospechosos
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"⚠️ Patrón sospechoso detectado: {pattern}")
                # En producción, podrías rechazar o sanitizar más agresivamente
        
        logger.info(f"✅ Texto validado: {len(text)} caracteres")
        return text
    
    @classmethod
    def sanitize_for_llm(cls, text: str) -> str:
        """
        Sanitiza texto antes de enviar al LLM
        
        Args:
            text: Texto a sanitizar
            
        Returns:
            Texto sanitizado
        """
        # Remover caracteres de control
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limitar longitud para tokens del LLM
        max_chars = 15000  # ~3750 tokens aproximadamente
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.info(f"Texto truncado a {max_chars} caracteres para LLM")
        
        return text
