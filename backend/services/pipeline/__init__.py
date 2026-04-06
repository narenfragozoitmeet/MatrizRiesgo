"""
Sistema de Pipeline de Ingesta Automática

Permite configurar y ejecutar pipelines para descargar documentos
de fuentes externas de forma periódica y almacenarlos en el sistema.
"""

from .manager import PipelineManager
from .scheduler import PipelineScheduler
from .base import DataSource, IngestionResult

__all__ = ['PipelineManager', 'PipelineScheduler', 'DataSource', 'IngestionResult']
