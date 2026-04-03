"""Service - Ingesta a Fuentes Internas

Responsabilidad:
- Analizar matrices aprobadas
- Extraer patrones y conocimiento
- Actualizar catálogos en Silver
- Mejorar base de conocimiento
"""

import logging
from typing import List, Dict, Any
from collections import Counter
import json

logger = logging.getLogger(__name__)

class KnowledgeIngestionService:
    """Servicio de ingesta de conocimiento desde matrices previas"""
    
    def __init__(self):
        self.name = "KnowledgeIngestionService"
    
    def extract_patterns_from_matrices(self, matrices: List[Dict]) -> Dict[str, Any]:
        """Extrae patrones de matrices aprobadas
        
        Args:
            matrices: Lista de matrices aprobadas de las últimas 24h
            
        Returns:
            Dict con patrones identificados
        """
        logger.info(f"Analizando {len(matrices)} matrices para extraer patrones...")
        
        patterns = {
            "peligros_frecuentes": {},
            "controles_efectivos": {},
            "combinaciones_peligro_riesgo": [],
            "sectores_analizados": set(),
            "mejores_practicas": []
        }
        
        # Contadores
        peligros_counter = Counter()
        controles_counter = Counter()
        
        for matriz in matrices:
            empresa = matriz.get("nombre_empresa", "")
            riesgos = matriz.get("riesgos", [])
            
            for riesgo in riesgos:
                # Extraer peligro
                peligro = riesgo.get("peligro", {})
                clasificacion = peligro.get("clasificacion", "")
                descripcion = peligro.get("descripcion", "")
                
                # Contar peligros frecuentes
                peligros_counter[f"{clasificacion}:{descripcion}"] += 1
                
                # Extraer controles propuestos
                controles_propuestos = riesgo.get("controles_propuestos", [])
                for control in controles_propuestos:
                    jerarquia = control.get("jerarquia", "")
                    descripcion_control = control.get("descripcion", "")
                    controles_counter[f"{jerarquia}:{descripcion_control}"] += 1
                
                # Combinaciones peligro-riesgo
                riesgo_desc = riesgo.get("riesgo", {}).get("descripcion_riesgo", "")
                if riesgo_desc:
                    patterns["combinaciones_peligro_riesgo"].append({
                        "peligro": descripcion,
                        "clasificacion": clasificacion,
                        "riesgo": riesgo_desc
                    })
        
        # Top 20 peligros más frecuentes
        patterns["peligros_frecuentes"] = dict(peligros_counter.most_common(20))
        
        # Top 20 controles más efectivos
        patterns["controles_efectivos"] = dict(controles_counter.most_common(20))
        
        logger.info(f"Patrones extraídos: {len(patterns['peligros_frecuentes'])} peligros frecuentes, "
                   f"{len(patterns['controles_efectivos'])} controles efectivos")
        
        return patterns
    
    async def update_catalog_peligros(self, patterns: Dict[str, Any], db_session) -> int:
        """Actualiza catálogo de peligros en Silver
        
        Args:
            patterns: Patrones extraídos
            db_session: Sesión de base de datos
            
        Returns:
            Número de registros actualizados
        """
        logger.info("Actualizando catálogo de peligros en Silver...")
        
        peligros_frecuentes = patterns.get("peligros_frecuentes", {})
        updated_count = 0
        
        # TODO: Implementar actualización real en Silver
        # for peligro_key, frecuencia in peligros_frecuentes.items():
        #     clasificacion, descripcion = peligro_key.split(":", 1)
        #     
        #     # Buscar o crear en catalogo_peligros
        #     peligro_record = db_session.query(CatalogoPeligro).filter_by(
        #         clasificacion=clasificacion,
        #         descripcion=descripcion
        #     ).first()
        #     
        #     if peligro_record:
        #         # Actualizar frecuencia/metadata
        #         peligro_record.metadata_json["frecuencia"] = frecuencia
        #         updated_count += 1
        #     else:
        #         # Crear nuevo
        #         nuevo_peligro = CatalogoPeligro(
        #             clasificacion=clasificacion,
        #             descripcion=descripcion,
        #             metadata_json={"frecuencia": frecuencia, "aprendido": True}
        #         )
        #         db_session.add(nuevo_peligro)
        #         updated_count += 1
        # 
        # db_session.commit()
        
        logger.info(f"Catálogo de peligros actualizado: {updated_count} registros")
        return updated_count
    
    async def update_catalog_controles(self, patterns: Dict[str, Any], db_session) -> int:
        """Actualiza catálogo de controles en Silver
        
        Args:
            patterns: Patrones extraídos
            db_session: Sesión de base de datos
            
        Returns:
            Número de registros actualizados
        """
        logger.info("Actualizando catálogo de controles en Silver...")
        
        controles_efectivos = patterns.get("controles_efectivos", {})
        updated_count = 0
        
        # TODO: Implementar actualización real en Silver
        # Similar a update_catalog_peligros pero para CatalogoControl
        
        logger.info(f"Catálogo de controles actualizado: {updated_count} registros")
        return updated_count
    
    async def save_learned_patterns(self, patterns: Dict[str, Any], db_session) -> str:
        """Guarda patrones aprendidos para uso futuro
        
        Args:
            patterns: Patrones extraídos
            db_session: Sesión de base de datos
            
        Returns:
            ID del registro de patrones
        """
        logger.info("Guardando patrones aprendidos...")
        
        import uuid
        from datetime import datetime
        
        pattern_id = str(uuid.uuid4())
        
        # TODO: Crear tabla patterns_learned en Silver
        # pattern_record = PatternsLearned(
        #     id=pattern_id,
        #     fecha_aprendizaje=datetime.utcnow(),
        #     patterns_json=patterns,
        #     num_matrices_analizadas=len(patterns.get("sectores_analizados", [])),
        #     version="1.0"
        # )
        # db_session.add(pattern_record)
        # db_session.commit()
        
        logger.info(f"Patrones guardados: {pattern_id}")
        return pattern_id
    
    async def ingest_knowledge(self, db_session) -> Dict[str, Any]:
        """Proceso completo de ingesta de conocimiento
        
        Args:
            db_session: Sesión de base de datos
            
        Returns:
            Resultado de la ingesta
        """
        try:
            logger.info("Iniciando ingesta de conocimiento...")
            
            # 1. Obtener matrices aprobadas de las últimas 24 horas
            # TODO: Consultar Gold
            # from datetime import datetime, timedelta
            # fecha_limite = datetime.utcnow() - timedelta(hours=24)
            # matrices = db_session.query(MatrizGTC45).filter(
            #     MatrizGTC45.estado == "approved",
            #     MatrizGTC45.fecha_aprobacion >= fecha_limite
            # ).all()
            
            matrices = []  # Placeholder
            
            if not matrices:
                logger.info("No hay matrices nuevas aprobadas para analizar")
                return {"status": "no_data", "matrices_analizadas": 0}
            
            # 2. Extraer patrones
            patterns = self.extract_patterns_from_matrices(
                [m.__dict__ for m in matrices] if matrices else []
            )
            
            # 3. Actualizar catálogos
            peligros_updated = await self.update_catalog_peligros(patterns, db_session)
            controles_updated = await self.update_catalog_controles(patterns, db_session)
            
            # 4. Guardar patrones
            pattern_id = await self.save_learned_patterns(patterns, db_session)
            
            result = {
                "status": "success",
                "matrices_analizadas": len(matrices),
                "peligros_actualizados": peligros_updated,
                "controles_actualizados": controles_updated,
                "pattern_id": pattern_id,
                "top_peligros": list(patterns["peligros_frecuentes"].keys())[:5],
                "top_controles": list(patterns["controles_efectivos"].keys())[:5]
            }
            
            logger.info(f"Ingesta completada: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error en ingesta de conocimiento: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }