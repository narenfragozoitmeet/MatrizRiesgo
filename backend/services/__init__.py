"""
Servicios del backend

Servicios activos:
- excel_generator: Generación de archivos Excel para matrices
- pipeline: Sistema de ingesta automática
"""

from .excel_generator import excel_generator

__all__ = ['excel_generator']
