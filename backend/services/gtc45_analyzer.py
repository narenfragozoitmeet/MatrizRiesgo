import os
import logging
from typing import List, Tuple
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

from models.gtc45_models import (
    Proceso, Actividad, Tarea, Peligro, ValoracionGTC45, 
    Control, RiesgoGTC45, MatrizGTC45
)
from services.gtc45_calculator import (
    calcular_np, calcular_nr, obtener_nivel_nd, 
    obtener_nivel_ne, obtener_nivel_nc
)
import uuid
from datetime import datetime, timezone

load_dotenv()
logger = logging.getLogger(__name__)

CATALOGO_PELIGROS = {
    "Físico": ["Ruido", "Iluminación", "Vibración", "Temperaturas extremas", "Radiación ionizante", "Radiación no ionizante", "Presión atmosférica"],
    "Químico": ["Polvos orgánicos", "Polvos inorgánicos", "Fibras", "Líquidos", "Gases y vapores", "Humos metálicos", "Material particulado"],
    "Biológico": ["Virus", "Bacterias", "Hongos", "Ricketsias", "Parásitos", "Picaduras", "Mordeduras", "Fluidos o excrementos"],
    "Biomecánico": ["Postura prolongada", "Movimiento repetitivo", "Esfuerzo", "Manipulación manual de cargas"],
    "Psicosocial": ["Gestión organizacional", "Características del grupo social", "Condiciones de la tarea", "Interfase persona-tarea", "Jornada de trabajo", "Carga mental"],
    "Condiciones de Seguridad": [
        "Mecánico", "Eléctrico", "Locativo", "Tecnológico", 
        "Accidentes de tránsito", "Públicos", "Trabajo en alturas", 
        "Espacios confinados", "Explosión", "Incendio"
    ],
    "Fenómenos Naturales": ["Sismo", "Terremoto", "Vendaval", "Inundación", "Derrumbe", "Precipitaciones"]
}

async def analizar_documento_gtc45(text_content: str, document_name: str, empresa: str = "Empresa") -> MatrizGTC45:
    """Analiza documento y genera matriz GTC 45 completa"""
    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"gtc45-{document_name}-{uuid.uuid4()}",
            system_message=f"""Eres un experto en Seguridad y Salud en el Trabajo (SST) especializado en la metodología GTC 45:2012 de Colombia.

Tu tarea es analizar documentos empresariales (procedimientos, descripciones de cargo, perfiles de puesto) y generar una matriz de identificación de peligros y valoración de riesgos completa.

**METODOLOGÍA GTC 45:2012:**

**FÓRMULAS:**
- NP (Nivel Probabilidad) = ND (Nivel Deficiencia) × NE (Nivel Exposición)
- NR (Nivel Riesgo) = NP × NC (Nivel Consecuencia)

**ESCALAS:**

ND - Nivel de Deficiencia:
- 10: Muy Alto (situación deficiente, no existen medidas preventivas)
- 6: Alto (situación deficiente, medidas de baja eficacia)
- 2: Medio (situación mejorable, medidas parciales)

NE - Nivel de Exposición:
- 4: Continua (sin interrupción o varias veces prolongadas)
- 3: Frecuente (varias veces durante la jornada por tiempos cortos)
- 2: Ocasional (alguna vez durante la jornada)
- 1: Esporádica (muy eventual)

NC - Nivel de Consecuencia:
- 100: Mortal o Catastrófico
- 60: Muy Grave (lesiones graves irreparables, incapacidad permanente)
- 25: Grave (incapacidad laboral temporal)
- 10: Leve (lesiones sin incapacidad)

**CATEGORÍAS DE PELIGROS:**
{json.dumps(CATALOGO_PELIGROS, indent=2, ensure_ascii=False)}

**JERARQUÍA DE CONTROLES (en orden de prioridad):**
1. Eliminación: Eliminar completamente el peligro
2. Sustitución: Reemplazar por algo menos peligroso
3. Controles de Ingeniería: Barreras físicas, ventilación, guardas
4. Controles Administrativos: Procedimientos, capacitación, señalización, rotación
5. EPP: Equipos de protección personal (último recurso)

**FORMATO DE RESPUESTA JSON:**
{{
  "procesos": [
    {{
      "nombre": "Nombre del proceso",
      "actividades": [
        {{
          "nombre": "Nombre actividad",
          "tipo": "Rutinaria" o "No Rutinaria",
          "tareas": [
            {{
              "nombre": "Nombre tarea",
              "descripcion": "Descripción detallada",
              "peligros": [
                {{
                  "clasificacion": "Físico/Químico/Biológico/Biomecánico/Psicosocial/Condiciones de Seguridad/Fenómenos Naturales",
                  "descripcion": "Descripción específica del peligro",
                  "fuente": "Fuente generadora del peligro",
                  "efectos_posibles": ["Efecto 1", "Efecto 2"],
                  "valoracion": {{
                    "nd_valor": 10/6/2,
                    "nd_justificacion": "Por qué este valor",
                    "ne_valor": 4/3/2/1,
                    "ne_justificacion": "Por qué este valor",
                    "nc_valor": 100/60/25/10,
                    "nc_justificacion": "Por qué este valor"
                  }},
                  "controles_existentes": [
                    {{"jerarquia": "Eliminación/Sustitución/Ingeniería/Administrativo/EPP", "descripcion": "Control actual"}}
                  ],
                  "controles_recomendados": [
                    {{"jerarquia": "Eliminación/Sustitución/Ingeniería/Administrativo/EPP", "descripcion": "Control sugerido"}}
                  ]
                }}
              ]
            }}
          ]
        }}
      ]
    }}
  ],
  "resumen_ejecutivo": "Resumen general del análisis (2-3 párrafos)"
}}

Sé exhaustivo. Identifica TODOS los peligros posibles. Justifica cada valoración."""
        )
        
        chat.with_model("gemini", "gemini-2.5-flash")
        
        user_message = UserMessage(
            text=f"""Analiza el siguiente documento y genera una matriz GTC 45 completa:

EMPRESA: {empresa}
DOCUMENTO: {document_name}

CONTENIDO:
{text_content[:50000]}

Genera el análisis en formato JSON como se especificó."""
        )
        
        response = await chat.send_message(user_message)
        logger.info(f"Raw AI response length: {len(response)}")
        
        response_text = response.strip()
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_text = response_text[json_start:json_end + 1]
        else:
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            json_text = response_text.strip()
        
        result = json.loads(json_text)
        
        # Procesar y estructurar resultados
        riesgos_lista = []
        
        for proceso_data in result.get("procesos", []):
            proceso = Proceso(
                nombre=proceso_data["nombre"],
                descripcion=proceso_data.get("descripcion")
            )
            
            for actividad_data in proceso_data.get("actividades", []):
                actividad = Actividad(
                    nombre=actividad_data["nombre"],
                    tipo=actividad_data.get("tipo", "Rutinaria"),
                    proceso=proceso.nombre
                )
                
                for tarea_data in actividad_data.get("tareas", []):
                    tarea = Tarea(
                        nombre=tarea_data["nombre"],
                        descripcion=tarea_data.get("descripcion", ""),
                        actividad=actividad.nombre
                    )
                    
                    for peligro_data in tarea_data.get("peligros", []):
                        peligro = Peligro(
                            clasificacion=peligro_data["clasificacion"],
                            descripcion=peligro_data["descripcion"],
                            fuente=peligro_data.get("fuente"),
                            efectos_posibles=peligro_data.get("efectos_posibles", [])
                        )
                        
                        val_data = peligro_data["valoracion"]
                        nd_valor = val_data["nd_valor"]
                        ne_valor = val_data["ne_valor"]
                        nc_valor = val_data["nc_valor"]
                        
                        # Calcular NP y NR
                        np_valor, np_nivel = calcular_np(nd_valor, ne_valor)
                        nr_valor, interpretacion, interpretacion_texto, aceptabilidad = calcular_nr(np_valor, nc_valor)
                        
                        valoracion = ValoracionGTC45(
                            nd_valor=nd_valor,
                            nd_nivel=obtener_nivel_nd(nd_valor),
                            nd_justificacion=val_data.get("nd_justificacion", ""),
                            ne_valor=ne_valor,
                            ne_nivel=obtener_nivel_ne(ne_valor),
                            ne_justificacion=val_data.get("ne_justificacion", ""),
                            np_valor=np_valor,
                            np_nivel=np_nivel,
                            nc_valor=nc_valor,
                            nc_nivel=obtener_nivel_nc(nc_valor),
                            nc_justificacion=val_data.get("nc_justificacion", ""),
                            nr_valor=nr_valor,
                            interpretacion=interpretacion,
                            interpretacion_texto=interpretacion_texto,
                            aceptabilidad=aceptabilidad
                        )
                        
                        controles_exist = [
                            Control(**ctrl) for ctrl in peligro_data.get("controles_existentes", [])
                        ]
                        
                        controles_recom = [
                            Control(**ctrl) for ctrl in peligro_data.get("controles_recomendados", [])
                        ]
                        
                        riesgo = RiesgoGTC45(
                            id=str(uuid.uuid4()),
                            proceso=proceso,
                            actividad=actividad,
                            tarea=tarea,
                            peligro=peligro,
                            valoracion=valoracion,
                            controles_existentes=controles_exist,
                            controles_recomendados=controles_recom
                        )
                        
                        riesgos_lista.append(riesgo)
        
        # Calcular estadísticas
        estadisticas = calcular_estadisticas(riesgos_lista)
        
        matriz = MatrizGTC45(
            id=str(uuid.uuid4()),
            nombre_empresa=empresa,
            documento_origen=document_name,
            fecha_elaboracion=datetime.now(timezone.utc).isoformat(),
            responsable_elaboracion="Sistema Riesgo IA",
            riesgos=riesgos_lista,
            resumen_ejecutivo=result.get("resumen_ejecutivo", "Análisis completado."),
            estadisticas=estadisticas,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        return matriz
        
    except Exception as e:
        logger.error(f"Error analyzing document GTC45: {e}", exc_info=True)
        raise Exception(f"Error en el análisis GTC 45: {str(e)}")

def calcular_estadisticas(riesgos: List[RiesgoGTC45]) -> dict:
    """Calcula estadísticas de la matriz"""
    total = len(riesgos)
    
    por_interpretacion = {"I": 0, "II": 0, "III": 0, "IV": 0}
    por_clasificacion = {}
    por_aceptabilidad = {"Aceptable": 0, "Aceptable con control": 0, "No Aceptable": 0}
    
    for riesgo in riesgos:
        inter = riesgo.valoracion.interpretacion
        por_interpretacion[inter] = por_interpretacion.get(inter, 0) + 1
        
        clas = riesgo.peligro.clasificacion
        por_clasificacion[clas] = por_clasificacion.get(clas, 0) + 1
        
        acep = riesgo.valoracion.aceptabilidad
        por_aceptabilidad[acep] = por_aceptabilidad.get(acep, 0) + 1
    
    return {
        "total_riesgos": total,
        "por_interpretacion": por_interpretacion,
        "por_clasificacion": por_clasificacion,
        "por_aceptabilidad": por_aceptabilidad,
        "criticos": por_interpretacion["I"],
        "altos": por_interpretacion["II"],
        "medios": por_interpretacion["III"],
        "bajos": por_interpretacion["IV"]
    }