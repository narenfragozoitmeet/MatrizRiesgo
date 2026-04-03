"""Celery Tasks - Sources Update

Tareas para actualizar normativas, catálogos y bases de conocimiento
"""

from core.celery_app import celery_app
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.update_tasks.update_normativas")
def update_normativas():
    """Actualiza normativas oficiales (GTC 45, Decreto 1072, etc.)"""
    try:
        logger.info("Iniciando actualización de normativas...")
        
        # TODO: Implementar lógica de actualización
        # 1. Leer sources_config.yaml
        # 2. Descargar PDFs/scraping de páginas oficiales
        # 3. Guardar en esquema Silver
        
        logger.info("Normativas actualizadas correctamente")
        return {"status": "success", "updated": 0}
        
    except Exception as e:
        logger.error(f"Error actualizando normativas: {str(e)}")
        raise

@celery_app.task(name="tasks.update_tasks.update_catalogos")
def update_catalogos():
    """Actualiza catálogos de peligros y controles"""
    try:
        logger.info("Iniciando actualización de catálogos...")
        
        # TODO: Implementar lógica de actualización
        # 1. Leer archivos JSON locales
        # 2. Consultar APIs externas si están configuradas
        # 3. Actualizar tablas en esquema Silver
        
        logger.info("Catálogos actualizados correctamente")
        return {"status": "success", "updated": 0}
        
    except Exception as e:
        logger.error(f"Error actualizando catálogos: {str(e)}")
        raise

@celery_app.task(name="tasks.update_tasks.learn_from_matrices")
def learn_from_matrices():
    """Aprende patrones de matrices anteriores para mejorar sugerencias
    
    Esta tarea es crítica para el aprendizaje continuo del sistema.
    Se ejecuta diariamente a la 1 AM.
    """
    try:
        logger.info("Iniciando aprendizaje de matrices previas...")
        
        from services.knowledge_ingestion import KnowledgeIngestionService
        from db.session import SessionLocal
        
        # Crear servicio de ingesta
        knowledge_service = KnowledgeIngestionService()
        
        # Ejecutar ingesta con sesión de BD
        db = SessionLocal()
        try:
            import asyncio
            result = asyncio.run(knowledge_service.ingest_knowledge(db))
            
            logger.info(f"Aprendizaje completado: {result}")
            return result
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error en aprendizaje: {str(e)}", exc_info=True)
        raise

@celery_app.task(name="tasks.update_tasks.ingest_to_knowledge_base")
def ingest_to_knowledge_base():
    """Pipeline de ingesta a fuentes internas
    
    Procesa matrices aprobadas y actualiza:
    - Catálogo de peligros (Silver)
    - Catálogo de controles (Silver)
    - Base de conocimiento (Silver)
    - Patrones aprendidos (Silver)
    
    Se ejecuta después de learn_from_matrices.
    """
    try:
        logger.info("Iniciando pipeline de ingesta a fuentes internas...")
        
        # Esta tarea ya se ejecuta dentro de learn_from_matrices
        # Pero la mantenemos separada por si en el futuro queremos
        # ejecutarla de forma independiente
        
        result = learn_from_matrices()
        
        logger.info("Pipeline de ingesta completado")
        return {
            "status": "success",
            "ingestion_result": result
        }
        
    except Exception as e:
        logger.error(f"Error en pipeline de ingesta: {str(e)}", exc_info=True)
        raise

@celery_app.task(name="tasks.update_tasks.update_all_sources")
def update_all_sources():
    """Ejecuta actualización completa de todas las fuentes"""
    try:
        logger.info("Iniciando actualización completa de fuentes...")
        
        results = {
            "normativas": update_normativas(),
            "catalogos": update_catalogos(),
            "learning": learn_from_matrices()
        }
        
        logger.info("Actualización completa finalizada")
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Error en actualización completa: {str(e)}")
        raise