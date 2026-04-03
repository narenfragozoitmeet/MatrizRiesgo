"""API v1 - Ingestion Endpoint

POST /api/v1/ingest - Inicia el flujo asincrónico del grafo de agentes
GET /api/v1/tasks/{task_id} - Consulta estado de tarea en Redis/Celery
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from tasks.ingestion_tasks import process_document_graph
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class IngestResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[str] = None

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    empresa: str = Form(...)
):
    """Ingesta un documento y lanza el grafo de agentes asincrónicamente
    
    Args:
        file: Documento PDF, Word o Excel
        empresa: Nombre de la empresa
        
    Returns:
        task_id: ID para consultar el estado de la tarea
    """
    try:
        # Validar tipo de archivo
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Tipo de archivo no soportado. Use PDF, Word o Excel."
            )
        
        # Generar task_id
        task_id = str(uuid.uuid4())
        
        # Leer archivo
        file_content = await file.read()
        
        # Lanzar tarea Celery asincrónica
        task = process_document_graph.delay(
            task_id=task_id,
            filename=file.filename,
            content_type=file.content_type,
            file_data=file_content,
            empresa=empresa
        )
        
        logger.info(f"Tarea de ingesta iniciada: {task_id}")
        
        return IngestResponse(
            task_id=task_id,
            status="pending",
            message="Documento recibido. Procesamiento iniciado."
        )
        
    except Exception as e:
        logger.error(f"Error en ingesta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Consulta el estado de una tarea de procesamiento
    
    Args:
        task_id: ID de la tarea
        
    Returns:
        Estado actual, progreso y resultado (si está completo)
    """
    try:
        from celery.result import AsyncResult
        from core.celery_app import celery_app
        
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == "PENDING":
            response = TaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress={"message": "Tarea en cola..."}
            )
        elif task_result.state == "STARTED":
            response = TaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=task_result.info or {"message": "Procesando documento..."}
            )
        elif task_result.state == "SUCCESS":
            response = TaskStatusResponse(
                task_id=task_id,
                status="completed",
                result=task_result.result
            )
        elif task_result.state == "FAILURE":
            response = TaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(task_result.info)
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress={"state": task_result.state}
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error consultando tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))