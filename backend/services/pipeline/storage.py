"""
Gestión de almacenamiento para documentos descargados por el pipeline.
"""

import os
import aiofiles
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PipelineStorage:
    """Gestiona el almacenamiento de documentos descargados."""
    
    def __init__(self, base_path: str = "/app/data/pipeline_ingestion"):
        """
        Args:
            base_path: Directorio base para almacenar documentos
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crea los directorios necesarios si no existen."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "pending").mkdir(exist_ok=True)
        (self.base_path / "processed").mkdir(exist_ok=True)
        (self.base_path / "failed").mkdir(exist_ok=True)
    
    async def save_pending_document(self, 
                                    source_id: str, 
                                    filename: str, 
                                    content: bytes) -> str:
        """
        Guarda un documento descargado en estado pendiente.
        
        Args:
            source_id: ID de la fuente de datos
            filename: Nombre del archivo
            content: Contenido del archivo en bytes
            
        Returns:
            Ruta completa del archivo guardado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{source_id}_{filename}"
        file_path = self.base_path / "pending" / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Documento guardado: {file_path}")
        return str(file_path)
    
    def move_to_processed(self, pending_path: str) -> str:
        """
        Mueve un documento de pending a processed.
        
        Args:
            pending_path: Ruta del archivo pendiente
            
        Returns:
            Nueva ruta del archivo
        """
        pending = Path(pending_path)
        processed = self.base_path / "processed" / pending.name
        pending.rename(processed)
        logger.info(f"Movido a processed: {processed}")
        return str(processed)
    
    def move_to_failed(self, pending_path: str, error_msg: str) -> str:
        """
        Mueve un documento de pending a failed.
        
        Args:
            pending_path: Ruta del archivo pendiente
            error_msg: Mensaje de error
            
        Returns:
            Nueva ruta del archivo
        """
        pending = Path(pending_path)
        failed = self.base_path / "failed" / pending.name
        pending.rename(failed)
        
        # Guardar log de error
        error_log = failed.with_suffix('.error.txt')
        error_log.write_text(f"{datetime.now().isoformat()}\n{error_msg}")
        
        logger.warning(f"Movido a failed: {failed}")
        return str(failed)
    
    def list_pending_documents(self) -> list[str]:
        """Lista todos los documentos pendientes de procesar."""
        pending_dir = self.base_path / "pending"
        return [str(f) for f in pending_dir.iterdir() if f.is_file()]
    
    def get_stats(self) -> dict:
        """Retorna estadísticas de almacenamiento."""
        return {
            'pending': len(list((self.base_path / "pending").iterdir())),
            'processed': len(list((self.base_path / "processed").iterdir())),
            'failed': len(list((self.base_path / "failed").iterdir()))
        }
