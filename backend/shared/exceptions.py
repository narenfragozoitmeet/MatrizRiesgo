"""Excepciones personalizadas para el sistema"""

class RiesgoIAException(Exception):
    """Excepción base para todas las excepciones del sistema"""
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class ValidationError(RiesgoIAException):
    """Error de validación de datos"""
    pass


class DocumentExtractionError(RiesgoIAException):
    """Error al extraer texto de documento"""
    pass


class LLMProcessingError(RiesgoIAException):
    """Error al procesar con LLM"""
    pass


class DatabaseError(RiesgoIAException):
    """Error de base de datos"""
    pass


class FileTooLargeError(ValidationError):
    """Archivo excede tamaño máximo"""
    pass


class UnsupportedFileTypeError(ValidationError):
    """Tipo de archivo no soportado"""
    pass


class MatrizNotFoundError(RiesgoIAException):
    """Matriz no encontrada"""
    pass
