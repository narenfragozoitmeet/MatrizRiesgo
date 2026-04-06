"""
Clases base abstractas para el sistema de pipeline de ingesta.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class IngestionResult:
    """Resultado de una ingesta de documentos."""
    success: bool
    source_name: str
    documents_downloaded: int
    documents_processed: int
    errors: List[str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'source_name': self.source_name,
            'documents_downloaded': self.documents_downloaded,
            'documents_processed': self.documents_processed,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }


class DataSource(ABC):
    """
    Clase abstracta para fuentes de datos.
    
    Cada fuente externa debe heredar de esta clase e implementar
    los métodos abstractos.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Args:
            source_id: Identificador único de la fuente
            config: Configuración específica de la fuente
        """
        self.source_id = source_id
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    async def fetch_documents(self) -> List[tuple[str, bytes]]:
        """
        Descarga documentos de la fuente externa.
        
        Returns:
            Lista de tuplas (nombre_archivo, contenido_bytes)
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Valida que la configuración de la fuente sea correcta.
        
        Returns:
            True si la configuración es válida
        """
        pass
    
    def get_display_name(self) -> str:
        """Retorna el nombre legible de la fuente."""
        return self.config.get('display_name', self.source_id)
    
    def is_enabled(self) -> bool:
        """Retorna si la fuente está habilitada."""
        return self.enabled
