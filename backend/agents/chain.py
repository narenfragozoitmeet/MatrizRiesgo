"""
Cadena de procesamiento completa usando agentes LangChain
"""

from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from .extractor import DocumentExtractorAgent
from .analyzer import HazardAnalyzerAgent
from .calculator import RiskCalculatorAgent
from core.config import settings
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MatrizProcessingChain:
    """
    Cadena principal que orquesta todos los agentes para generar una matriz SST.
    
    Flujo:
    1. ExtractorAgent: Extrae texto del documento
    2. AnalyzerAgent: Identifica peligros con LLM
    3. CalculatorAgent: Calcula niveles de riesgo
    4. Retorna matriz completa lista para guardar
    """
    
    def __init__(self):
        """Inicializa la cadena con todos los agentes"""
        logger.info("Inicializando MatrizProcessingChain")
        
        # Inicializar LLM (Gemini 2.5 Flash)
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL_NAME,
            google_api_key=settings.EMERGENT_LLM_KEY,
            temperature=0.1,  # Baja temperatura para respuestas consistentes
            max_output_tokens=8000
        )
        
        # Inicializar agentes
        self.extractor = DocumentExtractorAgent()
        self.analyzer = HazardAnalyzerAgent(llm=self.llm)
        self.calculator = RiskCalculatorAgent(llm=self.llm)
        
        logger.info("MatrizProcessingChain inicializada correctamente")
    
    async def process_document(
        self,
        file_data: bytes,
        filename: str,
        file_type: str,
        empresa: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa un documento completo y genera la matriz de riesgos.
        
        Args:
            file_data: Contenido del archivo en bytes
            filename: Nombre del archivo
            file_type: Tipo de archivo (pdf, docx, xlsx)
            empresa: Nombre de la empresa (opcional, se extrae si no se proporciona)
            
        Returns:
            Dict con la matriz completa lista para guardar en MongoDB
        """
        logger.info(
            "Iniciando procesamiento de documento",
            filename=filename,
            file_type=file_type,
            file_size=len(file_data)
        )
        
        try:
            # PASO 1: Extraer texto
            logger.info("PASO 1/3: Extrayendo texto del documento")
            extraction_result = await self.extractor.execute({
                "file_data": file_data,
                "file_type": file_type,
                "filename": filename
            })
            
            raw_text = extraction_result["raw_text"]
            
            # Si no se proporcionó empresa, intentar extraerla del texto
            if not empresa:
                empresa = await self._extract_company_name(raw_text)
            
            logger.info(
                "Texto extraído",
                chars=len(raw_text),
                pages=extraction_result.get("num_pages", 0),
                empresa=empresa
            )
            
            # PASO 2: Analizar peligros
            logger.info("PASO 2/3: Analizando peligros con LLM")
            analysis_result = await self.analyzer.execute({
                "raw_text": raw_text,
                "empresa": empresa
            })
            
            peligros = analysis_result["peligros"]
            logger.info(f"Peligros identificados: {len(peligros)}")
            
            # PASO 3: Calcular riesgos
            logger.info("PASO 3/3: Calculando niveles de riesgo")
            calculation_result = await self.calculator.execute({
                "peligros": peligros,
                "empresa": empresa
            })
            
            riesgos = calculation_result["riesgos"]
            stats = calculation_result["estadisticas"]
            
            logger.info(
                "Riesgos calculados",
                total=len(riesgos),
                criticos=stats["critico"],
                altos=stats["alto"],
                medios=stats["medio"],
                bajos=stats["bajo"]
            )
            
            # Construir matriz completa
            matriz = {
                "empresa": empresa,
                "documento_origen": filename,
                "metodologia": "GTC 45 + RAM",
                "fecha": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "estado": "completada",
                
                # Estadísticas
                "total_riesgos": len(riesgos),
                "riesgos_criticos": stats["critico"],
                "riesgos_altos": stats["alto"],
                "riesgos_medios": stats["medio"],
                "riesgos_bajos": stats["bajo"],
                
                # Riesgos detallados
                "riesgos": riesgos,
                
                # Metadatos
                "fuentes": [filename],
                "metadata": {
                    "extraction": extraction_result.get("metadata", {}),
                    "num_pages": extraction_result.get("num_pages", 0),
                    "chars_processed": len(raw_text),
                    "llm_model": settings.LLM_MODEL_NAME
                }
            }
            
            logger.info(
                "Matriz generada exitosamente",
                empresa=empresa,
                total_riesgos=len(riesgos)
            )
            
            return matriz
            
        except Exception as e:
            logger.error(
                "Error procesando documento",
                error=str(e),
                filename=filename,
                exc_info=True
            )
            raise
    
    async def _extract_company_name(self, text: str) -> str:
        """
        Extrae el nombre de la empresa del texto usando LLM.
        
        Args:
            text: Texto del documento
            
        Returns:
            Nombre de la empresa o "Empresa sin especificar"
        """
        try:
            # Limitar texto para la consulta
            text_sample = text[:3000]
            
            prompt = f"""Analiza el siguiente texto y extrae ÚNICAMENTE el nombre de la empresa.

Texto:
{text_sample}

Responde SOLO con el nombre de la empresa, nada más.
Si no encuentras el nombre, responde "Empresa sin especificar"."""
            
            response = await self.llm.ainvoke(prompt)
            empresa = response.content.strip()
            
            # Validar que no sea muy largo (probablemente no es el nombre)
            if len(empresa) > 100:
                empresa = "Empresa sin especificar"
            
            return empresa
            
        except Exception as e:
            logger.error(f"Error extrayendo nombre de empresa: {str(e)}")
            return "Empresa sin especificar"
