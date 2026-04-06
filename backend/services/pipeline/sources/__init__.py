"""
Fuentes de datos para el sistema de pipeline.

Este directorio contiene implementaciones específicas de DataSource.
Cada fuente externa debe implementar la interfaz DataSource.
"""

from .example_source import ExampleDataSource

__all__ = ['ExampleDataSource']
