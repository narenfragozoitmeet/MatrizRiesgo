"""
Scheduler para ejecutar pipelines de forma periódica.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional
from .manager import PipelineManager

logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Gestiona la ejecución programada de pipelines."""
    
    def __init__(self, pipeline_manager: PipelineManager):
        """
        Args:
            pipeline_manager: Instancia del gestor de pipelines
        """
        self.manager = pipeline_manager
        self.scheduler = AsyncIOScheduler()
        self._jobs = {}
    
    def add_schedule(self, 
                     source_id: str, 
                     cron_expression: str,
                     job_id: Optional[str] = None) -> str:
        """
        Agrega un horario para ejecutar una fuente específica.
        
        Args:
            source_id: ID de la fuente a ejecutar
            cron_expression: Expresión cron (ej: "0 9 * * 1" = Lunes 9:00)
            job_id: ID opcional para el job
            
        Returns:
            ID del job creado
        """
        job_id = job_id or f"pipeline_{source_id}"
        
        # Parsear expresión cron
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Expresión cron debe tener 5 campos: min hora dia mes dia_semana")
        
        minute, hour, day, month, day_of_week = parts
        
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )
        
        job = self.scheduler.add_job(
            func=self._execute_pipeline,
            trigger=trigger,
            args=[source_id],
            id=job_id,
            replace_existing=True
        )
        
        self._jobs[job_id] = {
            'source_id': source_id,
            'cron': cron_expression,
            'next_run': job.next_run_time
        }
        
        logger.info(f"Schedule agregado: {job_id} - {cron_expression}")
        return job_id
    
    async def _execute_pipeline(self, source_id: str):
        """Ejecuta el pipeline para una fuente específica."""
        logger.info(f"Ejecutando pipeline programado para: {source_id}")
        try:
            results = await self.manager.run_ingestion(source_id)
            for result in results:
                if result.success:
                    logger.info(f"Pipeline exitoso: {result.source_name} - {result.documents_downloaded} docs")
                else:
                    logger.error(f"Pipeline falló: {result.source_name} - Errores: {result.errors}")
        except Exception as e:
            logger.error(f"Error ejecutando pipeline {source_id}: {str(e)}")
    
    def remove_schedule(self, job_id: str) -> bool:
        """Elimina un schedule programado."""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self._jobs:
                del self._jobs[job_id]
            logger.info(f"Schedule eliminado: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando schedule {job_id}: {str(e)}")
            return False
    
    def start(self):
        """Inicia el scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Pipeline Scheduler iniciado")
    
    def stop(self):
        """Detiene el scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Pipeline Scheduler detenido")
    
    def get_schedules(self) -> dict:
        """Retorna todos los schedules configurados."""
        return self._jobs.copy()
