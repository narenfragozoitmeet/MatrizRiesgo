"""LangGraph - Grafo Principal GTC 45

Define el flujo de agentes para procesamiento de documentos
Arquitectura multi-agente con LangGraph
"""

from langgraph.graph import StateGraph, END
from graphs.state import AgentState
import logging

# Importar agentes con nombres descriptivos
from agents.agent_01_extractor import agent_01_extractor_node
from agents.agent_02_hazard_identifier import agent_02_hazard_identifier_node
from agents.agent_03_risk_mapper import agent_03_risk_mapper_node
from agents.agent_04_control_planner import agent_04_control_planner_node
from agents.node_05_calculator import node_05_calculator
from agents.node_06_builder import node_06_builder

logger = logging.getLogger(__name__)

def create_gtc45_graph() -> StateGraph:
    """Crea el grafo de procesamiento GTC 45
    
    Flujo secuencial:
    START 
      → Agent_01_Extractor (extrae texto)
      → Agent_02_Hazard_Identifier (identifica peligros)
      → Agent_03_Risk_Mapper (mapea riesgos)
      → Agent_04_Control_Planner (planifica controles)
      → Node_05_Calculator (cálculos determinísticos)
      → Node_06_Builder (construye matriz final)
      → END
    
    Returns:
        StateGraph compilado y listo para ejecutar
    """
    
    # Crear grafo
    workflow = StateGraph(AgentState)
    
    # Añadir nodos con nombres descriptivos
    workflow.add_node("extract", agent_01_extractor_node)
    workflow.add_node("identify_hazards", agent_02_hazard_identifier_node)
    workflow.add_node("map_risks", agent_03_risk_mapper_node)
    workflow.add_node("plan_controls", agent_04_control_planner_node)
    workflow.add_node("calculate", node_05_calculator)
    workflow.add_node("build", node_06_builder)
    
    # Definir flujo secuencial
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "identify_hazards")
    workflow.add_edge("identify_hazards", "map_risks")
    workflow.add_edge("map_risks", "plan_controls")
    workflow.add_edge("plan_controls", "calculate")
    workflow.add_edge("calculate", "build")
    workflow.add_edge("build", END)
    
    logger.info("Grafo GTC 45 creado con 6 nodos")
    
    return workflow.compile()

def execute_graph(graph: StateGraph, initial_state: AgentState, file_data: bytes) -> AgentState:
    """Ejecuta el grafo con el estado inicial
    
    Args:
        graph: Grafo compilado
        initial_state: Estado inicial con documento
        file_data: Bytes del archivo
        
    Returns:
        Estado final después de ejecutar todos los nodos
    """
    try:
        logger.info(f"[{initial_state.task_id}] Ejecutando grafo...")
        
        # Ejecutar grafo (pasando file_data al primer nodo)
        # TODO: Pasar file_data correctamente al nodo de extracción
        final_state = graph.invoke(initial_state)
        
        logger.info(f"[{initial_state.task_id}] Grafo completado")
        return final_state
        
    except Exception as e:
        logger.error(f"[{initial_state.task_id}] Error ejecutando grafo: {str(e)}", exc_info=True)
        initial_state.add_error(f"Error en grafo: {str(e)}")
        return initial_state
