"""
Gestor principal del sistema de pipelines de ingesta.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from .base import DataSource, IngestionResult
from .storage import PipelineStorage

logger = logging.getLogger(__name__)


class PipelineManager:
    """Gestiona múltiples pipelines de ingesta de datos."""
    
    def __init__(self, storage: Optional[PipelineStorage] = None):
        self.sources: Dict[str, DataSource] = {}
        self.storage = storage or PipelineStorage()
        self.execution_history: List[IngestionResult] = []
    
    def register_source(self, source: DataSource) -> None:
        """
        Registra una nueva fuente de datos en el manager.
        
        Args:
            source: Instancia de DataSource a registrar
        """
        if not source.validate_config():
            raise ValueError(f"Configuración inválida para fuente: {source.source_id}")
        
        self.sources[source.source_id] = source
        logger.info(f"Fuente registrada: {source.get_display_name()} ({source.source_id})")
    
    def unregister_source(self, source_id: str) -> None:
        """Elimina una fuente de datos del manager."""
        if source_id in self.sources:
            del self.sources[source_id]
            logger.info(f"Fuente eliminada: {source_id}")
    
    async def run_ingestion(self, source_id: Optional[str] = None) -> List[IngestionResult]:
        """
        Ejecuta el proceso de ingesta.
        
        Args:
            source_id: Si se especifica, solo ejecuta esa fuente.
                      Si es None, ejecuta todas las fuentes habilitadas.
        
        Returns:
            Lista de resultados de ingesta
        """
        results = []
        
        # Determinar qué fuentes ejecutar
        sources_to_run = {}
        if source_id:
            if source_id not in self.sources:
                logger.error(f"Fuente no encontrada: {source_id}")
                return results
            sources_to_run = {source_id: self.sources[source_id]}
        else:
            sources_to_run = {sid: src for sid, src in self.sources.items() if src.is_enabled()}
        
        # Ejecutar cada fuente
        for sid, source in sources_to_run.items():
            result = await self._run_source_ingestion(source)
            results.append(result)
            self.execution_history.append(result)
        
        return results
    
    async def _run_source_ingestion(self, source: DataSource) -> IngestionResult:
        """
        Ejecuta la ingesta para una fuente específica.
        
        Args:
            source: Fuente de datos a ejecutar
            
        Returns:
            Resultado de la ingesta
        """
        logger.info(f"Iniciando ingesta desde: {source.get_display_name()}")
        
        errors = []
        downloaded = 0
        processed = 0
        
        try:
            # Descargar documentos
            documents = await source.fetch_documents()
            downloaded = len(documents)
            logger.info(f"Descargados {downloaded} documentos de {source.source_id}")
            
            # Guardar documentos
            for filename, content in documents:
                try:
                    await self.storage.save_pending_document(
                        source.source_id,
                        filename,
                        content
                    )
                    processed += 1
                except Exception as e:
                    error_msg = f"Error guardando {filename}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            success = len(errors) == 0
            
        except Exception as e:
            error_msg = f"Error en ingesta de {source.source_id}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            success = False
        
        return IngestionResult(
            success=success,
            source_name=source.get_display_name(),
            documents_downloaded=downloaded,
            documents_processed=processed,
            errors=errors,
            timestamp=datetime.now()
        )
    
    async def process_pending_documents(self) -> dict:
        """
        Procesa todos los documentos pendientes.
        
        Nota: Actualmente solo mueve archivos a 'processed'.
        TODO: Integrar con SSTService para procesamiento real.
        
        Returns:
            Estadísticas del procesamiento
        """
        pending_files = self.storage.list_pending_documents()
        processed_count = 0
        failed_count = 0
        
        logger.info(f"Procesando {len(pending_files)} documentos pendientes")
        
        for file_path in pending_files:
            try:
                # Aquí se integraría con SSTService para procesar el documento
                # Por ahora solo movemos a processed
                self.storage.move_to_processed(file_path)
                processed_count += 1
            except Exception as e:
                self.storage.move_to_failed(file_path, str(e))
                failed_count += 1
                logger.error(f"Error procesando {file_path}: {str(e)}")
        
        return {
            'total': len(pending_files),
            'processed': processed_count,
            'failed': failed_count
        }
    
    def get_sources_status(self) -> List[dict]:
        """Retorna el estado de todas las fuentes registradas."""
        return [
            {
                'source_id': source.source_id,
                'display_name': source.get_display_name(),
                'enabled': source.is_enabled(),
                'config': source.config
            }
            for source in self.sources.values()
        ]
    
    def get_execution_history(self, limit: int = 10) -> List[dict]:
        """Retorna el historial de ejecuciones."""
        return [r.to_dict() for r in self.execution_history[-limit:]]
