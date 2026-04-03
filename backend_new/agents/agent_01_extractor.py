"""Agent 01 - Extractor de Texto

Responsabilidad:
- Extraer texto de documentos PDF, Word, Excel
- Limpiar y estructurar el texto
- Guardar en esquema Bronze
"""

import logging
from graphs.state import AgentState
from types.base_types import TaskStatus
from types.bronze_types import TextoExtraido
from prompts.agent_01_extractor_prompt import get_extraction_prompt

logger = logging.getLogger(__name__)

class Agent01Extractor:
    """Agente 01 - Extractor de texto de documentos"""
    
    def __init__(self):
        self.name = "Agent_01_Extractor"
    
    async def execute(self, state: AgentState, file_data: bytes) -> AgentState:
        """Ejecuta la extracción de texto
        
        Args:
            state: Estado actual del grafo
            file_data: Bytes del archivo
            
        Returns:
            Estado actualizado con texto extraído
        """
        try:
            logger.info(f"[{state.task_id}] {self.name} iniciado")
            state.update_status(TaskStatus.EXTRACTING)
            state.add_log(f"{self.name}: Extrayendo texto...")
            
            # TODO: Implementar extracción real
            # from services.document_parser import parse_document
            # raw_text = parse_document(file_data, state.documento.content_type)
            
            # Placeholder
            raw_text = "Texto extraído del documento..."
            
            # TODO: Llamar a LLM para limpiar texto
            # prompt = get_extraction_prompt(
            #     filename=state.documento.filename,
            #     content_type=state.documento.content_type,
            #     raw_text=raw_text
            # )
            # resultado = await llm.generate(prompt)
            
            # Crear resultado
            texto_extraido = TextoExtraido(
                texto_crudo=raw_text,
                texto_limpio=raw_text,  # TODO: texto limpio por LLM
                metadata={"source": "placeholder"},
                num_palabras=len(raw_text.split())
            )
            
            state.texto_extraido = texto_extraido
            state.add_log(f"{self.name}: Texto extraído exitosamente")
            
            # TODO: Guardar en Bronze schema
            # await save_to_bronze(state.task_id, texto_extraido)
            
            return state
            
        except Exception as e:
            logger.error(f"[{state.task_id}] Error en {self.name}: {str(e)}")
            state.add_error(f"{self.name}: {str(e)}")
            return state

# Función para usar en el grafo
async def agent_01_extractor_node(state: AgentState, file_data: bytes = None) -> AgentState:
    """Nodo del grafo para Agent 01"""
    agent = Agent01Extractor()
    return await agent.execute(state, file_data)