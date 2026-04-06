"""Servicio de Procesamiento de Matriz SST (GTC 45)"""

import json
import logging
from typing import Dict, Any
from services.llm_service import llm_service
from prompts.sst_prompts import (
    SYSTEM_MESSAGE_SST,
    PROMPT_IDENTIFICAR_PELIGROS_SST,
    PROMPT_EVALUAR_RIESGOS_SST
)
from models.matrices import MatrizSST, RiesgoSST, PeligroSST, NivelRiesgo

logger = logging.getLogger(__name__)

class MatrizSSTProcessor:
    """Procesador de Matriz SST usando agentes LLM"""
    
    async def procesar(
        self,
        texto_documento: str,
        nombre_documento: str,
        document_id: str
    ) -> MatrizSST:
        """
        Procesa documento completo y genera matriz SST
        Extrae automáticamente el nombre de la empresa del documento
        
        Returns:
            MatrizSST completa
        """
        try:
            logger.info(f"🔄 Iniciando procesamiento SST")
            
            # PASO 1: Identificar peligros Y extraer nombre empresa
            logger.info("📋 Paso 1/2: Identificando peligros SST y extrayendo empresa...")
            peligros_data = await self._identificar_peligros(
                texto_documento, nombre_documento
            )
            
            # Extraer nombre de empresa del resultado
            empresa = peligros_data.get("nombre_empresa", "Empresa Desconocida")
            
            # PASO 2: Evaluar riesgos
            logger.info("📊 Paso 2/2: Evaluando riesgos con GTC 45...")
            riesgos_data = await self._evaluar_riesgos(peligros_data)
            
            # PASO 3: Construir matriz
            matriz = self._construir_matriz(
                riesgos_data, empresa, nombre_documento, document_id
            )
            
            logger.info(f"✅ Matriz SST generada: {matriz.total_riesgos} riesgos")
            return matriz
            
        except Exception as e:
            logger.error(f"❌ Error procesando matriz SST: {str(e)}")
            raise
    
    async def _identificar_peligros(
        self, texto: str, nombre_doc: str
    ) -> Dict[str, Any]:
        """Agente 1: Identifica peligros SST en el texto Y extrae nombre empresa"""
        
        prompt = PROMPT_IDENTIFICAR_PELIGROS_SST.format(
            texto_documento=texto[:15000],  # Limitar tokens
            nombre_documento=nombre_doc
        )
        
        response = await llm_service.generate(
            prompt=prompt,
            system_message=SYSTEM_MESSAGE_SST,
            session_id=f"sst_identificar_{empresa}"
        )
        
        # Extraer JSON de la respuesta
        json_data = self._extract_json(response)
        return json_data
    
    async def _evaluar_riesgos(self, peligros_data: Dict) -> Dict[str, Any]:
        """Agente 2: Evalúa riesgos con metodología GTC 45"""
        
        prompt = PROMPT_EVALUAR_RIESGOS_SST.format(
            peligros_json=json.dumps(peligros_data, indent=2, ensure_ascii=False)
        )
        
        response = await llm_service.generate(
            prompt=prompt,
            system_message=SYSTEM_MESSAGE_SST,
            session_id=f"sst_evaluar"
        )
        
        json_data = self._extract_json(response)
        return json_data
    
    def _construir_matriz(
        self, riesgos_data: Dict, empresa: str, doc: str, doc_id: str
    ) -> MatrizSST:
        """Construye objeto MatrizSST a partir de datos evaluados"""
        
        riesgos = []
        stats = {"criticos": 0, "altos": 0, "medios": 0, "bajos": 0}
        
        for r_data in riesgos_data.get("riesgos_evaluados", []):
            # Crear peligro
            peligro = PeligroSST(
                clasificacion=r_data["peligro"]["clasificacion"],
                descripcion=r_data["peligro"]["descripcion"],
                fuente=r_data["peligro"].get("fuente", "N/A"),
                efectos_posibles=r_data["peligro"].get("efectos_posibles", [])
            )
            
            # Crear riesgo
            riesgo = RiesgoSST(
                id_riesgo=r_data["id_riesgo"],
                proceso=r_data["proceso"],
                zona_lugar=r_data["zona_lugar"],
                actividad=r_data["actividad"],
                peligro=peligro,
                nivel_deficiencia=r_data["nivel_deficiencia"],
                nivel_exposicion=r_data["nivel_exposicion"],
                nivel_probabilidad=r_data["nivel_probabilidad"],
                interpretacion_probabilidad=r_data["interpretacion_probabilidad"],
                nivel_consecuencia=r_data["nivel_consecuencia"],
                nivel_riesgo=r_data["nivel_riesgo"],
                interpretacion_riesgo=NivelRiesgo(r_data["interpretacion_riesgo"]),
                controles_existentes=r_data.get("controles_existentes", []),
                controles_propuestos=r_data.get("controles_propuestos", []),
                aceptabilidad=r_data.get("aceptabilidad", "Pendiente")
            )
            
            riesgos.append(riesgo)
            
            # Estadísticas
            nivel = r_data["interpretacion_riesgo"]
            if nivel == "Crítico":
                stats["criticos"] += 1
            elif nivel == "Alto":
                stats["altos"] += 1
            elif nivel == "Medio":
                stats["medios"] += 1
            else:
                stats["bajos"] += 1
        
        # Crear matriz
        matriz = MatrizSST(
            empresa=empresa,
            documento_origen=doc,
            document_id=doc_id,
            riesgos=riesgos,
            total_riesgos=len(riesgos),
            riesgos_criticos=stats["criticos"],
            riesgos_altos=stats["altos"],
            riesgos_medios=stats["medios"],
            riesgos_bajos=stats["bajos"]
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
matriz_sst_processor = MatrizSSTProcessor()
