import os
import logging
from typing import List, Tuple
from pydantic import BaseModel
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class RiskItem(BaseModel):
    categoria: str
    riesgo: str
    descripcion: str
    probabilidad: str
    impacto: str
    nivel_riesgo: str
    mitigacion: str

async def analyze_document_for_risks(text_content: str, document_name: str) -> Tuple[List[RiskItem], str]:
    """Analyze document content to extract legal risks using Gemini"""
    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"risk-analysis-{document_name}",
            system_message="""Eres un experto en análisis de riesgos legales corporativos. Tu tarea es analizar documentos empresariales e identificar todos los riesgos legales potenciales.

Debes estructurar tu análisis en formato JSON con la siguiente estructura:
{
  "risks": [
    {
      "categoria": "Categoría del riesgo (ej: Contractual, Cumplimiento Regulatorio, Laboral, Propiedad Intelectual, Fiscal, etc.)",
      "riesgo": "Nombre corto del riesgo",
      "descripcion": "Descripción detallada del riesgo identificado",
      "probabilidad": "Alta/Media/Baja",
      "impacto": "Alto/Medio/Bajo",
      "nivel_riesgo": "Crítico/Alto/Medio/Bajo",
      "mitigacion": "Recomendaciones para mitigar el riesgo"
    }
  ],
  "summary": "Resumen ejecutivo del análisis de riesgos (2-3 párrafos)"
}

Identifica TODOS los riesgos potenciales que encuentres en el documento. Sé exhaustivo y preciso."""
        )
        
        chat.with_model("gemini", "gemini-2.5-flash")
        
        user_message = UserMessage(
            text=f"""Analiza el siguiente documento y genera una matriz de riesgos legales completa:

DOCUMENTO: {document_name}

CONTENIDO:
{text_content[:50000]}

Proporciona el análisis en formato JSON como se especificó."""
        )
        
        response = await chat.send_message(user_message)
        
        logger.info(f"Raw AI response: {repr(response)}")
        
        response_text = response.strip()
        
        # Extract JSON from the response - look for JSON block
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_text = response_text[json_start:json_end + 1]
            logger.info(f"Extracted JSON: {repr(json_text[:200])}...")
        else:
            # Fallback to original cleaning logic
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            json_text = response_text.strip()
            logger.info(f"Cleaned response text: {repr(json_text[:200])}...")
        
        if not json_text:
            logger.error("Empty response from AI")
            raise Exception("AI returned empty response")
        
        result = json.loads(json_text)
        
        risks = [RiskItem(**risk) for risk in result.get("risks", [])]
        summary = result.get("summary", "Análisis completado.")
        
        if not risks:
            risks = [RiskItem(
                categoria="General",
                riesgo="Análisis Requerido",
                descripcion="No se identificaron riesgos específicos en el documento. Se recomienda revisión manual.",
                probabilidad="Baja",
                impacto="Bajo",
                nivel_riesgo="Bajo",
                mitigacion="Realizar revisión legal exhaustiva del documento."
            )]
        
        return risks, summary
    
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise Exception(f"Error en el análisis: {str(e)}")