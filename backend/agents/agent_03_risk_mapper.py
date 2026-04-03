"""Agent 03 - Mapeador de Riesgos

Responsabilidad:
- Asociar cada peligro con riesgos específicos
- Determinar efectos posibles y peor consecuencia
- Estimar personas expuestas
- Guardar en esquema Silver
"""

import logging
from graphs.state import AgentState
from types.base_types import TaskStatus
from types.silver_types import RiesgoMapeado
from prompts.agent_03_risk_mapper_prompt import get_risk_mapping_prompt
import json

logger = logging.getLogger(__name__)

class Agent03RiskMapper:
    """Agente 03 - Mapeador de riesgos"""
    
    def __init__(self):
        self.name = "Agent_03_Risk_Mapper"
    
    async def execute(self, state: AgentState) -> AgentState:
        """Mapea riesgos a partir de peligros
        
        Args:
            state: Estado con peligros_identificados
            
        Returns:
            Estado actualizado (riesgos se agregarán en siguiente paso)
        """
        try:
            logger.info(f"[{state.task_id}] {self.name} iniciado")
            state.update_status(TaskStatus.MAPPING_RISKS)
            state.add_log(f"{self.name}: Mapeando riesgos...")
            
            if not state.peligros_identificados:
                raise ValueError("No hay peligros identificados para mapear")
            
            # Convertir peligros a JSON para el prompt
            peligros_json = json.dumps(
                [p.dict() for p in state.peligros_identificados],
                indent=2,
                ensure_ascii=False
            )
            
            # TODO: Llamar a LLM
            # prompt = get_risk_mapping_prompt(peligros_json)
            # resultado = await llm.generate(prompt)
            # riesgos_data = parse_json(resultado)
            
            # Placeholder: crear riesgo de ejemplo
            # (Los riesgos se combinarán con peligros en Node_06_Builder)
            
            state.add_log(f"{self.name}: Mapeo completado")
            
            # TODO: Guardar en Silver schema
            # await save_to_silver_riesgos(state.task_id, riesgos_mapeados)
            
            return state
            
        except Exception as e:
            logger.error(f"[{state.task_id}] Error en {self.name}: {str(e)}")
            state.add_error(f"{self.name}: {str(e)}")
            return state

async def agent_03_risk_mapper_node(state: AgentState) -> AgentState:
    """Nodo del grafo para Agent 03"""
    agent = Agent03RiskMapper()
    return await agent.execute(state)