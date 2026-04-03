"""Agent 02 - Identificador de Peligros

Responsabilidad:
- Analizar texto limpio
- Identificar procesos, actividades, tareas
- Detectar peligros según GTC 45
- Guardar en esquema Silver
"""

import logging
from graphs.state import AgentState
from types.base_types import TaskStatus, TipoTarea, ClasificacionPeligro
from types.silver_types import PeligroIdentificado
from prompts.agent_02_hazard_identifier_prompt import get_hazard_identification_prompt
import uuid

logger = logging.getLogger(__name__)

class Agent02HazardIdentifier:
    """Agente 02 - Identificador de peligros"""
    
    def __init__(self):
        self.name = "Agent_02_Hazard_Identifier"
    
    async def execute(self, state: AgentState) -> AgentState:
        """Identifica peligros en el texto
        
        Args:
            state: Estado con texto_extraido
            
        Returns:
            Estado con peligros_identificados
        """
        try:
            logger.info(f"[{state.task_id}] {self.name} iniciado")
            state.update_status(TaskStatus.IDENTIFYING_HAZARDS)
            state.add_log(f"{self.name}: Identificando peligros...")
            
            if not state.texto_extraido:
                raise ValueError("No hay texto extraído para analizar")
            
            # TODO: Llamar a LLM con prompt
            # prompt = get_hazard_identification_prompt(
            #     empresa=state.documento.empresa,
            #     documento=state.documento.filename,
            #     texto_limpio=state.texto_extraido.texto_limpio
            # )
            # resultado = await llm.generate(prompt)
            # peligros_data = parse_json(resultado)
            
            # Placeholder: crear un peligro de ejemplo
            peligro_ejemplo = PeligroIdentificado(
                id=str(uuid.uuid4()),
                clasificacion=ClasificacionPeligro.FISICO,
                descripcion="Exposición a ruido en área de producción",
                fuente="Maquinaria industrial",
                medio="Aéreo",
                individuo="Sistema auditivo",
                proceso="Producción",
                zona_lugar="Planta de producción",
                actividad="Operación de maquinaria",
                tarea="Supervisión de línea de producción",
                tipo_tarea=TipoTarea.RUTINARIA,
                confianza=0.9
            )
            
            state.peligros_identificados = [peligro_ejemplo]
            state.add_log(f"{self.name}: {len(state.peligros_identificados)} peligros identificados")
            
            # TODO: Guardar en Silver schema
            # await save_to_silver_peligros(state.task_id, state.peligros_identificados)
            
            return state
            
        except Exception as e:
            logger.error(f"[{state.task_id}] Error en {self.name}: {str(e)}")
            state.add_error(f"{self.name}: {str(e)}")
            return state

async def agent_02_hazard_identifier_node(state: AgentState) -> AgentState:
    """Nodo del grafo para Agent 02"""
    agent = Agent02HazardIdentifier()
    return await agent.execute(state)