"""
Agente para análisis de peligros usando LLM
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .base import BaseAgent
import logging
import json

logger = logging.getLogger(__name__)


class PeligroIdentificado(BaseModel):
    """Modelo de peligro identificado según GTC 45"""
    peligro: str = Field(description="Descripción clara del peligro")
    clasificacion: str = Field(description="Clasificación según GTC 45: Biológico, Físico, Químico, Psicosocial, Biomecánico, Condiciones de seguridad, Fenómenos naturales")
    fuente: str = Field(description="Fuente generadora del peligro")
    actividad: str = Field(description="Actividad o proceso donde se presenta")
    area: str = Field(description="Área de trabajo afectada")
    efectos_posibles: str = Field(description="Posibles efectos en la salud")


class HazardAnalyzerAgent(BaseAgent):
    """
    Agente que usa LLM para identificar peligros laborales.
    
    Usa Gemini 2.5 Flash para:
    1. Leer el texto del documento
    2. Identificar peligros según metodología GTC 45
    3. Clasificar y estructurar los peligros
    """
    
    def __init__(self, llm, **kwargs):
        super().__init__(llm=llm, **kwargs)
        
        # Parser para output estructurado
        self.parser = JsonOutputParser(pydantic_object=PeligroIdentificado)
        
        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto en SST (Seguridad y Salud en el Trabajo) especializado en la metodología GTC 45 colombiana.

Tu tarea es identificar TODOS los peligros laborales mencionados en el documento.

Clasificaciones según GTC 45:
- Biológico: Virus, bacterias, hongos, parásitos
- Físico: Ruido, iluminación, temperatura, radiación, vibración
- Químico: Gases, vapores, polvos, humos, líquidos
- Psicosocial: Estrés, carga mental, acoso, turnos
- Biomecánico: Posturas, movimientos repetitivos, manipulación de cargas
- Condiciones de seguridad: Mecánico, eléctrico, locativo, tecnológico, accidentes de tránsito, público, trabajo en alturas
- Fenómenos naturales: Sismo, inundación, vendaval

Sé específico y detallado. Identifica peligros reales, no genéricos."""),
            ("human", """Empresa: {empresa}

Documento:
{text}

Identifica TODOS los peligros laborales presentes.

Responde ÚNICAMENTE con un array JSON de objetos con esta estructura:
{format_instructions}

Ejemplo:
[
  {{
    "peligro": "Exposición a ruido industrial superior a 85 dB",
    "clasificacion": "Físico",
    "fuente": "Maquinaria de corte y prensas hidráulicas",
    "actividad": "Operación de maquinaria en planta de producción",
    "area": "Planta de producción - Zona de corte",
    "efectos_posibles": "Pérdida auditiva, trauma acústico, estrés"
  }}
]
""")
        ])
        
        # Cadena LangChain
        self.chain = self.prompt | self.llm
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que exista raw_text"""
        if "raw_text" not in input_data:
            raise ValueError("Falta campo requerido: raw_text")
        
        if not input_data["raw_text"].strip():
            raise ValueError("El texto está vacío")
        
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identifica peligros en el texto.
        
        Args:
            input_data: {
                "raw_text": str,
                "empresa": str (opcional)
            }
            
        Returns:
            {
                "peligros": List[dict],
                "total_peligros": int,
                "empresa": str
            }
        """
        self.validate_input(input_data)
        
        text = input_data["raw_text"]
        empresa = input_data.get("empresa", "Empresa sin especificar")
        
        # Limitar texto para no exceder límites del LLM
        max_chars = 30000
        if len(text) > max_chars:
            logger.warning(f"Texto muy largo ({len(text)} chars), truncando a {max_chars}")
            text = text[:max_chars] + "\n\n[... documento truncado por límite de tamaño ...]"
        
        self.log_execution("started", text_length=len(text), empresa=empresa)
        
        try:
            # Invocar LLM
            response = await self.chain.ainvoke({
                "empresa": empresa,
                "text": text,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Parsear respuesta
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Intentar parsear JSON
            try:
                # Limpiar respuesta (a veces el LLM agrega markdown)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                peligros = json.loads(content)
                
                # Asegurar que es una lista
                if not isinstance(peligros, list):
                    peligros = [peligros]
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del LLM: {e}")
                logger.error(f"Respuesta del LLM: {content[:500]}...")
                # Retornar lista vacía en caso de error
                peligros = []
            
            self.log_execution(
                "completed",
                total_peligros=len(peligros)
            )
            
            return {
                "peligros": peligros,
                "total_peligros": len(peligros),
                "empresa": empresa
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de peligros: {str(e)}")
            raise
