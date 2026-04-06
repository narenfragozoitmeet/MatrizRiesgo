"""
Ejemplo de implementación de una fuente de datos.

Este archivo sirve como plantilla para crear nuevas fuentes.
"""

import logging
from typing import List, Dict, Any
from ..base import DataSource

logger = logging.getLogger(__name__)


class ExampleDataSource(DataSource):
    """
    Fuente de datos de ejemplo.
    
    Esta clase muestra cómo implementar una fuente personalizada.
    Cuando se definan las fuentes reales, se pueden crear clases
    similares (ej: SharePointSource, GoogleDriveSource, etc.)
    
    Configuración esperada:
    {
        'enabled': bool,
        'display_name': str,
        'url': str,  # URL de la fuente
        'credentials': {  # Credenciales si son necesarias
            'username': str,
            'password': str
        }
    }
    """
    
    def validate_config(self) -> bool:
        """Valida que la configuración tenga los campos requeridos."""
        required_fields = ['url']
        
        for field in required_fields:
            if field not in self.config:
                logger.error(f"Campo requerido faltante en config: {field}")
                return False
        
        return True
    
    async def fetch_documents(self) -> List[tuple[str, bytes]]:
        """
        Descarga documentos de la fuente.
        
        En una implementación real, aquí se haría:
        1. Conectar a la fuente externa (API, FTP, etc.)
        2. Listar documentos disponibles
        3. Descargar cada documento
        4. Retornar lista de (nombre, contenido)
        
        Returns:
            Lista de tuplas (nombre_archivo, contenido_bytes)
        """
        logger.info(f"Fetching documents from {self.config['url']}")
        
        # IMPLEMENTACIÓN PLACEHOLDER
        # En producción, aquí iría el código real de descarga
        
        documents = []
        
        # Ejemplo de cómo se retornaría:
        # documents.append(('documento1.pdf', pdf_bytes))
        # documents.append(('documento2.docx', docx_bytes))
        
        logger.info(f"Descargados {len(documents)} documentos de {self.source_id}")
        return documents
