"""
Agente para calcular niveles de riesgo según GTC 45 + RAM
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent
import logging
import json

logger = logging.getLogger(__name__)


class RiskCalculatorAgent(BaseAgent):
    """
    Agente que calcula niveles de riesgo usando:
    1. LLM para estimar ND (Nivel de Deficiencia), NE (Nivel de Exposición), NC (Nivel de Consecuencia)
    2. Fórmulas GTC 45 para calcular NR (Nivel de Riesgo)
    3. Clasificación RAM (Risk Assessment Matrix)
    """
    
    def __init__(self, llm, **kwargs):
        super().__init__(llm=llm, **kwargs)
        
        # Prompt para estimación de valores
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto en valoración de riesgos laborales según GTC 45.

Para cada peligro, debes estimar:

**ND - Nivel de Deficiencia:**
- 10: Muy Alto (sin medidas de control, condiciones muy deficientes)
- 6: Alto (deficiencias en controles, necesita mejoras)
- 2: Medio (controles parciales, aceptable)
- 0: Bajo (controles completos y efectivos)

**NE - Nivel de Exposición:**
- 4: Continua (todo el turno, más de 8 horas)
- 3: Frecuente (varias veces en el turno)
- 2: Ocasional (alguna vez en el turno)
- 1: Esporadica (raras veces al mes)

**NC - Nivel de Consecuencia:**
- 100: Mortal o catastrófico
- 60: Muy grave (lesiones graves, incapacidad permanente)
- 25: Grave (lesiones con incapacidad temporal)
- 10: Leve (lesiones menores)

Sé realista y conservador en las estimaciones."""),
            ("human", """Peligro a valorar:
- Peligro: {peligro}
- Clasificación: {clasificacion}
- Fuente: {fuente}
- Actividad: {actividad}
- Área: {area}
- Efectos posibles: {efectos_posibles}

Estima los valores y responde ÚNICAMENTE con JSON:
{{
  "ND": <2|6|10>,
  "NE": <1|2|3|4>,
  "NC": <10|25|60|100>,
  "justificacion_ND": "...",
  "justificacion_NE": "...",
  "justificacion_NC": "..."
}}
""")
        ])
        
        self.chain = self.prompt | self.llm
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que exista lista de peligros"""
        if "peligros" not in input_data:
            raise ValueError("Falta campo requerido: peligros")
        
        if not isinstance(input_data["peligros"], list):
            raise ValueError("peligros debe ser una lista")
        
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula niveles de riesgo para cada peligro.
        
        Args:
            input_data: {
                "peligros": List[dict],
                "empresa": str (opcional)
            }
            
        Returns:
            {
                "riesgos": List[dict],  # Peligros + cálculos
                "estadisticas": dict
            }
        """
        self.validate_input(input_data)
        
        peligros = input_data["peligros"]
        
        self.log_execution("started", total_peligros=len(peligros))
        
        riesgos_calculados = []
        stats = {
            "critico": 0,
            "alto": 0,
            "medio": 0,
            "bajo": 0
        }
        
        for idx, peligro in enumerate(peligros, 1):
            try:
                # Estimar valores con LLM
                response = await self.chain.ainvoke(peligro)
                content = response.content if hasattr(response, 'content') else str(response)
                
                # Parsear respuesta
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                estimacion = json.loads(content)
                
                # Extraer valores
                nd = estimacion.get("ND", 6)  # Default: medio
                ne = estimacion.get("NE", 2)  # Default: ocasional
                nc = estimacion.get("NC", 25)  # Default: grave
                
                # Calcular NP (Nivel de Probabilidad)
                np = nd * ne
                
                # Calcular NR (Nivel de Riesgo)
                nr = np * nc
                
                # Clasificar nivel de riesgo
                if nr >= 4000:
                    nivel = "Crítico"
                    stats["critico"] += 1
                elif nr >= 600:
                    nivel = "Alto"
                    stats["alto"] += 1
                elif nr >= 150:
                    nivel = "Medio"
                    stats["medio"] += 1
                else:
                    nivel = "Bajo"
                    stats["bajo"] += 1
                
                # Interpretación
                if nr >= 4000:
                    interpretacion = "Situación crítica. Intervención urgente."
                elif nr >= 600:
                    interpretacion = "Intervención urgente. Corregir inmediatamente."
                elif nr >= 150:
                    interpretacion = "Mejorar controles. Intervención a corto plazo."
                else:
                    interpretacion = "Mantener controles actuales. Vigilar periódicamente."
                
                # Agregar cálculos al peligro
                riesgo = {
                    **peligro,
                    "ND": nd,
                    "NE": ne,
                    "NC": nc,
                    "NP": np,
                    "NR": nr,
                    "nivel_riesgo": nivel,
                    "interpretacion": interpretacion,
                    "justificacion": {
                        "ND": estimacion.get("justificacion_ND", "N/A"),
                        "NE": estimacion.get("justificacion_NE", "N/A"),
                        "NC": estimacion.get("justificacion_NC", "N/A")
                    }
                }
                
                riesgos_calculados.append(riesgo)
                
                logger.info(
                    f"Riesgo {idx}/{len(peligros)} calculado",
                    nivel=nivel,
                    nr=nr
                )
                
            except Exception as e:
                logger.error(f"Error calculando riesgo {idx}: {str(e)}")
                # Continuar con el siguiente
                continue
        
        self.log_execution(
            "completed",
            total_calculados=len(riesgos_calculados),
            criticos=stats["critico"],
            altos=stats["alto"]
        )
        
        return {
            "riesgos": riesgos_calculados,
            "estadisticas": stats
        }
