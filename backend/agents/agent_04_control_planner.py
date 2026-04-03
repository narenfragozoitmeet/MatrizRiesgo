"""Agent 04 - Planificador de Controles

Responsabilidad:
- Identificar controles existentes
- Proponer controles nuevos según jerarquía GTC 45
- Priorizar y estimar costos/plazos
- Guardar en esquema Silver
"""

import logging
from graphs.state import AgentState
from types.base_types import TaskStatus
from prompts.agent_04_control_planner_prompt import get_control_planning_prompt
import json

logger = logging.getLogger(__name__)

class Agent04ControlPlanner:
    """Agente 04 - Planificador de controles"""
    
    def __init__(self):
        self.name = "Agent_04_Control_Planner"
    
    async def execute(self, state: AgentState) -> AgentState:
        """Planifica controles para los riesgos
        
        Args:
            state: Estado con riesgos mapeados
            
        Returns:
            Estado actualizado con controles
        """
        try:
            logger.info(f"[{state.task_id}] {self.name} iniciado")
            state.update_status(TaskStatus.PLANNING_CONTROLS)
            state.add_log(f"{self.name}: Planificando controles...")
            
            # TODO: Preparar datos para el prompt
            # riesgos_json = json.dumps(...)
            # texto_original = state.texto_extraido.texto_limpio
            
            # TODO: Llamar a LLM
            # prompt = get_control_planning_prompt(riesgos_json, texto_original)
            # resultado = await llm.generate(prompt)
            # controles_data = parse_json(resultado)
            
            state.add_log(f"{self.name}: Controles planificados")
            
            # TODO: Guardar en Silver schema
            # await save_to_silver_controles(state.task_id, controles)
            
            return state
            
        except Exception as e:
            logger.error(f"[{state.task_id}] Error en {self.name}: {str(e)}")
            state.add_error(f"{self.name}: {str(e)}")
            return state

async def agent_04_control_planner_node(state: AgentState) -> AgentState:
    """Nodo del grafo para Agent 04"""
    agent = Agent04ControlPlanner()
    return await agent.execute(state)