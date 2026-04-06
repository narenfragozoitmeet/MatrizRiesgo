"""Servicio de Procesamiento de Matriz de Riesgos Legales"""

import json
import logging
from typing import Dict, Any
from services.llm_service import llm_service
from prompts.legal_prompts import (
    SYSTEM_MESSAGE_LEGAL,
    PROMPT_IDENTIFICAR_RIESGOS_LEGALES,
    PROMPT_EVALUAR_RIESGOS_LEGALES
)
from models.matrices import MatrizLegal, RiesgoLegal, CategoriaRiesgoLegal, NivelRiesgo

logger = logging.getLogger(__name__)

class MatrizLegalProcessor:
    """Procesador de Matriz de Riesgos Legales usando agentes LLM"""
    
    async def procesar(
        self,
        texto_documento: str,
        empresa: str,
        nombre_documento: str,
        document_id: str
    ) -> MatrizLegal:
        """
        Procesa documento completo y genera matriz de riesgos legales
        
        Returns:
            MatrizLegal completa
        """
        try:
            logger.info(f"🔄 Iniciando procesamiento Legal para {empresa}")
            
            # PASO 1: Identificar riesgos legales
            logger.info("📋 Paso 1/2: Identificando riesgos legales...")
            riesgos_data = await self._identificar_riesgos(
                texto_documento, empresa, nombre_documento
            )
            
            # PASO 2: Evaluar y cuantificar riesgos
            logger.info("📊 Paso 2/2: Evaluando riesgos con RAM...")
            riesgos_evaluados = await self._evaluar_riesgos(riesgos_data)
            
            # PASO 3: Construir matriz
            matriz = self._construir_matriz(
                riesgos_evaluados, empresa, nombre_documento, document_id
            )
            
            logger.info(f"✅ Matriz Legal generada: {matriz.total_riesgos} riesgos")
            return matriz
            
        except Exception as e:
            logger.error(f"❌ Error procesando matriz legal: {str(e)}")
            raise
    
    async def _identificar_riesgos(
        self, texto: str, empresa: str, nombre_doc: str
    ) -> Dict[str, Any]:
        """Agente 1: Identifica riesgos legales en el texto"""
        
        prompt = PROMPT_IDENTIFICAR_RIESGOS_LEGALES.format(
            texto_documento=texto[:15000],  # Limitar tokens
            empresa=empresa,
            nombre_documento=nombre_doc
        )
        
        response = await llm_service.generate(
            prompt=prompt,
            system_message=SYSTEM_MESSAGE_LEGAL,
            session_id=f"legal_identificar_{empresa}"
        )
        
        # Extraer JSON de la respuesta
        json_data = self._extract_json(response)
        return json_data
    
    async def _evaluar_riesgos(self, riesgos_data: Dict) -> Dict[str, Any]:
        """Agente 2: Evalúa riesgos con metodología RAM"""
        
        prompt = PROMPT_EVALUAR_RIESGOS_LEGALES.format(
            riesgos_json=json.dumps(riesgos_data, indent=2, ensure_ascii=False)
        )
        
        response = await llm_service.generate(
            prompt=prompt,
            system_message=SYSTEM_MESSAGE_LEGAL,
            session_id=f"legal_evaluar"
        )
        
        json_data = self._extract_json(response)
        return json_data
    
    def _construir_matriz(
        self, riesgos_data: Dict, empresa: str, doc: str, doc_id: str
    ) -> MatrizLegal:
        """Construye objeto MatrizLegal a partir de datos evaluados"""
        
        riesgos = []
        stats = {"criticos": 0, "altos": 0, "medios": 0, "bajos": 0}
        categorias = {}
        
        for r_data in riesgos_data.get("riesgos_evaluados", []):
            # Determinar nivel de riesgo
            nivel_calc = r_data["nivel_riesgo_calculado"]
            if nivel_calc >= 20:
                nivel = NivelRiesgo.CRITICO
            elif nivel_calc >= 12:
                nivel = NivelRiesgo.ALTO
            elif nivel_calc >= 6:
                nivel = NivelRiesgo.MEDIO
            elif nivel_calc >= 3:
                nivel = NivelRiesgo.BAJO
            else:
                nivel = NivelRiesgo.TRIVIAL
            
            # Crear riesgo
            riesgo = RiesgoLegal(
                id_riesgo=r_data["id_riesgo"],
                categoria=CategoriaRiesgoLegal(r_data["categoria"]),
                descripcion=r_data["descripcion"],
                fuente_documento=r_data.get("fuente_documento", "N/A"),
                probabilidad_ocurrencia=r_data["probabilidad_ocurrencia"],
                impacto_financiero=r_data["impacto_financiero"],
                impacto_reputacional=r_data["impacto_reputacional"],
                impacto_operacional=r_data["impacto_operacional"],
                nivel_riesgo_calculado=nivel_calc,
                nivel_riesgo=nivel,
                normativa_aplicable=r_data.get("normativa_aplicable", []),
                clausulas_relevantes=r_data.get("clausulas_relevantes", []),
                controles_actuales=r_data.get("controles_actuales", []),
                acciones_mitigacion=r_data.get("acciones_mitigacion", []),
                responsable_sugerido=r_data.get("responsable_sugerido", "Legal/Compliance"),
                prioridad=r_data.get("prioridad", "Media")
            )
            
            riesgos.append(riesgo)
            
            # Estadísticas
            if nivel == NivelRiesgo.CRITICO:
                stats["criticos"] += 1
            elif nivel == NivelRiesgo.ALTO:
                stats["altos"] += 1
            elif nivel == NivelRiesgo.MEDIO:
                stats["medios"] += 1
            else:
                stats["bajos"] += 1
            
            # Contar categorías
            cat = r_data["categoria"]
            categorias[cat] = categorias.get(cat, 0) + 1
        
        # Crear matriz
        matriz = MatrizLegal(
            empresa=empresa,
            documento_origen=doc,
            document_id=doc_id,
            riesgos=riesgos,
            total_riesgos=len(riesgos),
            riesgos_criticos=stats["criticos"],
            riesgos_altos=stats["altos"],
            riesgos_medios=stats["medios"],
            riesgos_bajos=stats["bajos"],
            distribucion_categorias=categorias
        )
        
        return matriz
    
    def _extract_json(self, text: str) -> Dict:
        """Extrae JSON de respuesta del LLM"""
        try:
            # Buscar JSON en bloques de código
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                json_str = text[start:end].strip()
            else:
                # Buscar por llaves
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error extrayendo JSON: {str(e)}")
            logger.debug(f"Respuesta: {text[:500]}")
            raise ValueError(f"No se pudo extraer JSON válido de la respuesta del LLM")

# Instancia singleton
matriz_legal_processor = MatrizLegalProcessor()
