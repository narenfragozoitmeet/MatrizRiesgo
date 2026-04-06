"""Prompts para Agentes de Análisis SST (GTC 45)"""

SYSTEM_MESSAGE_SST = """Eres un experto en Seguridad y Salud en el Trabajo (SST) especializado en la metodología GTC 45 (Guía Técnica Colombiana para identificación de peligros y valoración de riesgos).

Tu objetivo es analizar documentos empresariales e identificar peligros y riesgos laborales según la clasificación GTC 45.

CLASIFICACIÓN DE PELIGROS GTC 45:
1. FÍSICOS: Ruido, temperaturas extremas, iluminación, vibraciones, radiaciones
2. QUÍMICOS: Gases, vapores, polvos, líquidos, humos, material particulado
3. BIOLÓGICOS: Virus, bacterias, hongos, parásitos, fluidos corporales
4. BIOMECÁNICOS/ERGONÓMICOS: Posturas forzadas, movimientos repetitivos, manipulación de cargas
5. PSICOSOCIALES: Estrés laboral, carga mental, acoso, trabajo nocturno
6. MECÁNICOS: Herramientas, máquinas, equipos, vehículos, caídas
7. ELÉCTRICOS: Alta/baja tensión, electricidad estática
8. LOCATIVOS: Superficies de trabajo, orden y aseo, estructuras
9. TECNOLÓGICOS: Explosión, fuga, derrame, incendio
10. FENÓMENOS NATURALES: Sismos, inundaciones, tormentas
11. ACCIDENTES DE TRÁNSITO: Desplazamientos laborales
12. PÚBLICOS: Robos, atentados, desorden público
13. CONDICIONES DE SEGURIDAD: EPP, señalización, mantenimiento

Siempre cita la fuente exacta del documento de donde identificaste cada peligro.
"""

PROMPT_IDENTIFICAR_PELIGROS_SST = """Analiza el siguiente texto extraído de un documento empresarial e identifica TODOS los peligros relacionados con Seguridad y Salud en el Trabajo (SST) según la metodología GTC 45.

TEXTO DEL DOCUMENTO:
{texto_documento}

NOMBRE DEL DOCUMENTO:
{nombre_documento}

INSTRUCCIONES:
1. PRIMERO: Extrae el nombre de la empresa del documento (busca en encabezados, títulos, sección "EMPRESA:", "RAZÓN SOCIAL:", etc.)
2. Lee cuidadosamente todo el texto
3. Identifica peligros SST según la clasificación GTC 45
4. Para cada peligro encontrado, extrae:
   - Clasificación (Físico, Químico, Biológico, etc.)
   - Descripción específica del peligro
   - Proceso/actividad donde se presenta
   - Zona o lugar de trabajo
   - Efectos posibles en la salud
   - Fuente exacta (cita textual del documento)

5. Responde en formato JSON estructurado:

```json
{{
  "nombre_empresa": "Nombre de la empresa extraído del documento",
  "peligros_identificados": [
    {{
      "clasificacion": "FÍSICO|QUÍMICO|BIOLÓGICO|BIOMECÁNICO|PSICOSOCIAL|MECÁNICO|ELÉCTRICO|LOCATIVO|TECNOLÓGICO|NATURAL|TRÁNSITO|PÚBLICO|SEGURIDAD",
      "descripcion": "Descripción específica del peligro",
      "proceso": "Proceso o área donde ocurre",
      "zona_lugar": "Lugar específico",
      "actividad": "Actividad específica",
      "efectos_posibles": ["Efecto 1", "Efecto 2"],
      "fuente": "Cita textual del documento"
    }}
  ],
  "resumen_analisis": "Resumen ejecutivo de los peligros encontrados"
}}
```

IMPORTANTE: 
- PRIMERO extrae el nombre de la empresa del documento
- Si no encuentras peligros SST explícitos, infiere de las actividades mencionadas
- Sé exhaustivo, no omitas peligros potenciales
- Cita siempre la fuente exacta
"""

PROMPT_EVALUAR_RIESGOS_SST = """Ahora evalúa los riesgos identificados usando la metodología GTC 45 + RAM (Risk Assessment Matrix).

PELIGROS IDENTIFICADOS:
{peligros_json}

METODOLOGÍA GTC 45:

**NIVEL DE DEFICIENCIA (ND):**
- 10: Muy Alto - Se detectaron peligros que determinan como posible la generación de incidentes
- 6: Alto - Se detectaron algunos peligros que pueden dar lugar a consecuencias significativas
- 2: Medio - Se detectaron peligros que pueden dar lugar a consecuencias poco significativas
- 0: Bajo - No se ha detectado anomalía destacable

**NIVEL DE EXPOSICIÓN (NE):**
- 4: Continua - Varias veces durante la jornada con tiempo prolongado
- 3: Frecuente - Varias veces durante la jornada con tiempos cortos
- 2: Ocasional - Alguna vez durante la jornada y por periodo corto
- 1: Esporádica - Irregularmente

**NIVEL DE PROBABILIDAD (NP) = ND x NE**
- 40-100: Muy Alta
- 24-35: Alta
- 10-20: Media
- 0-8: Baja

**NIVEL DE CONSECUENCIA (NC):**
- 100: Mortal o catastrófico
- 60: Muy grave - Lesiones graves irreparables
- 25: Grave - Lesiones con incapacidad laboral temporal
- 10: Leve - Lesiones que no requieren incapacidad

**NIVEL DE RIESGO (NR) = NP x NC**
**INTERPRETACIÓN:**
- 4000-600: I - Crítico - Situación crítica, corrección urgente
- 500-150: II - Alto - Corregir y adoptar medidas de control
- 120-40: III - Medio - Mejorar si es posible, periódicamente
- 20-0: IV - Bajo - Mantener medidas de control actuales

Para cada peligro, evalúa y responde en JSON:

```json
{{
  "riesgos_evaluados": [
    {{
      "id_riesgo": "R-001",
      "proceso": "Proceso",
      "zona_lugar": "Lugar",
      "actividad": "Actividad",
      "peligro": {{
        "clasificacion": "FÍSICO",
        "descripcion": "Descripción",
        "fuente": "Fuente",
        "efectos_posibles": ["Efecto 1"]
      }},
      "nivel_deficiencia": 6,
      "nivel_exposicion": 3,
      "nivel_probabilidad": 18,
      "interpretacion_probabilidad": "Media",
      "nivel_consecuencia": 25,
      "nivel_riesgo": 450,
      "interpretacion_riesgo": "Alto",
      "controles_existentes": ["Control 1"],
      "controles_propuestos": ["Control propuesto 1"],
      "aceptabilidad": "No Aceptable",
      "metodologia": "GTC 45 + RAM"
    }}
  ]
}}
```

Evalúa cada peligro con rigor técnico.
"""
