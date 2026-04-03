"""API v1 - Sources Endpoint

POST /api/v1/sources/update - Lanza pipeline de actualización manual
GET /api/v1/sources/status - Estado del último update
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from tasks.update_tasks import update_all_sources
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SourcesUpdateResponse(BaseModel):
    task_id: str
    status: str
    message: str

class SourcesStatusResponse(BaseModel):
    last_update: Optional[str] = None
    next_scheduled: Optional[str] = None
    sources_count: int
    status: str

@router.post("/sources/update", response_model=SourcesUpdateResponse)
async def trigger_sources_update():
    """Lanza manualmente el pipeline de actualización de fuentes
    
    Actualiza normativas, catálogos y bases de conocimiento desde sources_config.yaml
    
    Returns:
        task_id de la tarea de actualización
    """
    try:
        task = update_all_sources.delay()
        
        logger.info(f"Pipeline de fuentes iniciado: {task.id}")
        
        return SourcesUpdateResponse(
            task_id=task.id,
            status="started",
            message="Actualización de fuentes iniciada"
        )
        
    except Exception as e:
        logger.error(f"Error iniciando actualización de fuentes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/status", response_model=SourcesStatusResponse)
async def get_sources_status():
    """Obtiene el estado de las fuentes de conocimiento
    
    Returns:
        Información sobre última actualización y próxima programada
    """
    try:
        # TODO: Implementar consulta real desde base de datos
        return SourcesStatusResponse(
            last_update=None,
            next_scheduled=None,
            sources_count=0,
            status="pending_implementation"
        )
        
    except Exception as e:
        logger.error(f"Error consultando estado de fuentes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))