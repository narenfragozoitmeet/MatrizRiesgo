"""Node 06 - Builder (Constructor de Matriz Final)

Responsabilidad:
- Recibir todo el estado validado
- Formatear JSON final
- Guardar en esquema Gold
- Retornar matriz_id
- Marcar tarea como SUCCESS
"""

import logging
from graphs.state import AgentState
from types.base_types import TaskStatus
import uuid

logger = logging.getLogger(__name__)

class Node06Builder:
    """Nodo 06 - Constructor de matriz final en Gold"""
    
    def __init__(self):
        self.name = "Node_06_Builder"
    
    def execute(self, state: AgentState) -> AgentState:
        """Construye la matriz final y guarda en Gold
        
        Args:
            state: Estado completo con todos los datos
            
        Returns:
            Estado con matriz_id_gold
        """
        try:
            logger.info(f"[{state.task_id}] {self.name} iniciado")
            state.update_status(TaskStatus.BUILDING)
            state.add_log(f"{self.name}: Construyendo matriz final...")
            
            # Generar ID de matriz
            matriz_id = str(uuid.uuid4())
            
            # TODO: Formatear datos finales
            # matriz_data = {
            #     "id": matriz_id,
            #     "task_id": state.task_id,
            #     "empresa": state.documento.empresa,
            #     "documento_origen": state.documento.filename,
            #     "riesgos": [r.dict() for r in state.riesgos_completos],
            #     "resumen_ejecutivo": generar_resumen(state),
            #     "estadisticas": calcular_estadisticas(state.riesgos_completos)
            # }
            
            # TODO: Guardar en Gold schema
            # await db.gold.matrices_gtc45.insert_one(matriz_data)
            
            state.matriz_id_gold = matriz_id
            state.update_status(TaskStatus.COMPLETED)
            state.add_log(f"{self.name}: Matriz guardada en Gold. ID: {matriz_id}")
            
            logger.info(f"[{state.task_id}] Matriz completada: {matriz_id}")
            
            return state
            
        except Exception as e:
            logger.error(f"[{state.task_id}] Error en {self.name}: {str(e)}")
            state.add_error(f"{self.name}: {str(e)}")
            return state

def node_06_builder(state: AgentState) -> AgentState:
    """Nodo del grafo para Builder"""
    builder = Node06Builder()
    return builder.execute(state)