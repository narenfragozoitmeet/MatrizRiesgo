"""
API endpoints para gestión de pipelines de ingesta automática.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from core.config import settings

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])

# Se inicializará desde server.py
pipeline_manager = None
pipeline_scheduler = None


class ScheduleRequest(BaseModel):
    """Request para agregar/modificar un schedule."""
    source_id: str
    cron_expression: str


class ManualRunRequest(BaseModel):
    """Request para ejecutar manualmente un pipeline."""
    source_id: Optional[str] = None  # Si es None, ejecuta todas las fuentes


@router.get("/status")
async def get_pipeline_status(request: Request):
    """
    Obtiene el estado general del sistema de pipelines.
    """
    if not pipeline_manager:
        raise HTTPException(status_code=503, detail="Pipeline manager no inicializado")
    
    storage_stats = pipeline_manager.storage.get_stats()
    sources_status = pipeline_manager.get_sources_status()
    schedules = pipeline_scheduler.get_schedules() if pipeline_scheduler else {}
    
    return {
        "pipeline_enabled": True,
        "sources": sources_status,
        "storage": storage_stats,
        "schedules": schedules,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/sources")
async def list_sources(request: Request):
    """
    Lista todas las fuentes de datos registradas.
    """
    if not pipeline_manager:
        raise HTTPException(status_code=503, detail="Pipeline manager no inicializado")
    
    return {
        "sources": pipeline_manager.get_sources_status()
    }


@router.get("/history")
async def get_execution_history(request: Request, limit: int = 20):
    """
    Obtiene el historial de ejecuciones de pipelines.
    """
    if not pipeline_manager:
        raise HTTPException(status_code=503, detail="Pipeline manager no inicializado")
    
    return {
        "history": pipeline_manager.get_execution_history(limit=limit)
    }


@router.post("/run")
async def run_pipeline_manually(request: Request, body: ManualRunRequest):
    """
    Ejecuta manualmente un pipeline de ingesta.
    """
    if not pipeline_manager:
        raise HTTPException(status_code=503, detail="Pipeline manager no inicializado")
    
    try:
        results = await pipeline_manager.run_ingestion(body.source_id)
        return {
            "success": True,
            "results": [r.to_dict() for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando pipeline: {str(e)}")


@router.post("/schedule")
async def add_schedule(request: Request, body: ScheduleRequest):
    """
    Agrega o modifica un schedule para una fuente.
    """
    if not pipeline_scheduler:
        raise HTTPException(status_code=503, detail="Pipeline scheduler no inicializado")
    
    try:
        job_id = pipeline_scheduler.add_schedule(
            source_id=body.source_id,
            cron_expression=body.cron_expression
        )
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Schedule configurado para {body.source_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error configurando schedule: {str(e)}")


@router.delete("/schedule/{job_id}")
async def remove_schedule(request: Request, job_id: str):
    """
    Elimina un schedule configurado.
    """
    if not pipeline_scheduler:
        raise HTTPException(status_code=503, detail="Pipeline scheduler no inicializado")
    
    success = pipeline_scheduler.remove_schedule(job_id)
    
    if success:
        return {"success": True, "message": f"Schedule {job_id} eliminado"}
    else:
        raise HTTPException(status_code=404, detail=f"Schedule {job_id} no encontrado")


@router.post("/process-pending")
async def process_pending_documents(request: Request):
    """
    Procesa todos los documentos pendientes en el storage.
    """
    if not pipeline_manager:
        raise HTTPException(status_code=503, detail="Pipeline manager no inicializado")
    
    # TODO: Integrar con SSTService cuando se implemente el procesamiento
    stats = {
        "message": "Función en desarrollo. Integrar con SSTService para procesar documentos",
        "storage_stats": pipeline_manager.storage.get_stats()
    }
    
    return stats
