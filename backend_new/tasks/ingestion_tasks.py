"""Celery Tasks - Ingestion

Tarea principal que ejecuta el grafo de agentes LangGraph
"""

from core.celery_app import celery_app
from graphs.gtc45_graph import create_gtc45_graph, execute_graph
from graphs.state import AgentState, DocumentoIngesta, TaskStatus
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="tasks.ingestion_tasks.process_document_graph")
def process_document_graph(self, task_id: str, filename: str, content_type: str, file_data: bytes, empresa: str):
    """Procesa un documento a través del grafo de agentes
    
    Esta tarea orquesta el flujo completo:
    1. Agent_Extractor
    2. Agent_Hazard_ID
    3. Agent_Risk_Mapper
    4. Agent_Control_Planner
    5. Node_Calculator
    6. Node_Builder
    
    Args:
        task_id: ID único de la tarea
        filename: Nombre del archivo original
        content_type: Tipo MIME
        file_data: Contenido del archivo en bytes
        empresa: Nombre de la empresa
        
    Returns:
        dict con matriz_id y estadísticas
    """
    try:
        logger.info(f"[{task_id}] Iniciando procesamiento de {filename}")
        
        # Actualizar progreso
        self.update_state(
            state="STARTED",
            meta={"status": "initializing", "message": "Preparando grafo de agentes..."}
        )
        
        # TODO: Guardar archivo en Bronze (storage)
        document_id = str(uuid.uuid4())
        storage_path = f"bronze/documents/{task_id}/{filename}"
        
        # Crear estado inicial
        initial_state = AgentState(
            task_id=task_id,
            status=TaskStatus.PENDING,
            documento=DocumentoIngesta(
                document_id=document_id,
                filename=filename,
                content_type=content_type,
                storage_path=storage_path,
                empresa=empresa,
                fecha_carga=datetime.utcnow()
            ),
            config={"empresa": empresa}
        )
        
        # Crear y ejecutar grafo
        logger.info(f"[{task_id}] Creando grafo de agentes...")
        graph = create_gtc45_graph()
        
        logger.info(f"[{task_id}] Ejecutando grafo...")
        final_state = execute_graph(graph, initial_state, file_data)
        
        # Verificar resultado
        if final_state.status == TaskStatus.FAILED:
            logger.error(f"[{task_id}] Grafo falló: {final_state.errors}")
            raise Exception(f"Procesamiento fallido: {'; '.join(final_state.errors)}")
        
        if not final_state.matriz_id_gold:
            logger.error(f"[{task_id}] No se generó matriz_id_gold")
            raise Exception("No se pudo generar la matriz final")
        
        logger.info(f"[{task_id}] Procesamiento completado. Matriz: {final_state.matriz_id_gold}")
        
        # Resultado final
        return {
            "status": "success",
            "matriz_id": final_state.matriz_id_gold,
            "total_riesgos": len(final_state.riesgos_completos),
            "empresa": empresa,
            "documento": filename,
            "logs": final_state.logs[-10:]  # Últimos 10 logs
        }
        
    except Exception as e:
        logger.error(f"[{task_id}] Error en procesamiento: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise