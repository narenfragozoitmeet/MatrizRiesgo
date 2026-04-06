"""Prompts para Agentes de Análisis de Riesgos Legales"""

SYSTEM_MESSAGE_LEGAL = """Eres un experto abogado corporativo especializado en identificación y valoración de riesgos legales empresariales.

Tu objetivo es analizar documentos (contratos, políticas, procedimientos, informes) e identificar riesgos legales que puedan afectar a la organización.

CATEGORÍAS DE RIESGOS LEGALES:
1. CONTRACTUAL: Incumplimientos, cláusulas ambiguas, penalizaciones, garantías
2. CUMPLIMIENTO NORMATIVO: Violación de leyes, regulaciones, normativas sectoriales
3. LABORAL: Relaciones laborales, despidos, acoso, discriminación, seguridad social
4. FISCAL: Impuestos, declaraciones, evasión, sanciones tributarias
5. REGULATORIO: Licencias, permisos, autorizaciones, certificaciones
6. PROPIEDAD INTELECTUAL: Marcas, patentes, derechos de autor, secretos industriales
7. AMBIENTAL: Contaminación, manejo de residuos, permisos ambientales
8. PROTECCIÓN DE DATOS: GDPR, LOPDGDD, habeas data, privacidad
9. CORPORATIVO: Gobierno corporativo, responsabilidad de administradores
10. LITIGIOS: Demandas potenciales, conflictos judiciales, arbitrajes

Siempre cita la fuente exacta del documento (cláusula, sección, artículo).
"""

PROMPT_IDENTIFICAR_RIESGOS_LEGALES = """Analiza el siguiente texto extraído de un documento empresarial e identifica TODOS los riesgos legales potenciales.

TEXTO DEL DOCUMENTO:
{texto_documento}

INFORMACIÓN DE LA EMPRESA:
- Nombre: {empresa}
- Documento: {nombre_documento}

INSTRUCCIONES:
1. Lee cuidadosamente todo el texto
2. Identifica riesgos legales en todas las categorías aplicables
3. Para cada riesgo, extrae:
   - Categoría del riesgo legal
   - Descripción detallada del riesgo
   - Normativa aplicable (leyes, regulaciones)
   - Cláusulas o secciones relevantes del documento
   - Consecuencias potenciales (financieras, reputacionales, operacionales)
   - Fuente exacta (cita textual)

4. Responde en formato JSON estructurado:

```json
{{
  "riesgos_identificados": [
    {{
      "categoria": "CONTRACTUAL|CUMPLIMIENTO|LABORAL|FISCAL|REGULATORIO|PROPIEDAD_INTELECTUAL|AMBIENTAL|PROTECCION_DATOS|CORPORATIVO|LITIGIOS",
      "descripcion": "Descripción detallada del riesgo legal",
      "normativa_aplicable": ["Ley X", "Decreto Y"],
      "clausulas_relevantes": ["Cláusula 5.2", "Artículo 10"],
      "consecuencias_potenciales": {{
        "financieras": "Multas de hasta $X",
        "reputacionales": "Daño a imagen corporativa",
        "operacionales": "Suspensión de operaciones"
      }},
      "fuente_documento": "Cita textual del documento"
    }}
  ],
  "resumen_ejecutivo": "Resumen de los principales riesgos legales identificados"
}}
```

IMPORTANTE:
- Identifica tanto riesgos explícitos como implícitos
- Considera ausencia de cláusulas como riesgo (ej: falta de cláusula de confidencialidad)
- Analiza exposición a responsabilidades legales
- Sé exhaustivo y detallado
"""

PROMPT_EVALUAR_RIESGOS_LEGALES = """Ahora evalúa y cuantifica los riesgos legales identificados usando metodología RAM (Risk Assessment Matrix) adaptada al contexto legal.

RIESGOS IDENTIFICADOS:
{riesgos_json}

METODOLOGÍA RAM PARA RIESGOS LEGALES:

**PROBABILIDAD DE OCURRENCIA (1-5):**
- 5: Muy Alta - Riesgo inminente, condiciones presentes
- 4: Alta - Probable que ocurra en el corto plazo
- 3: Media - Podría ocurrir eventualmente
- 2: Baja - Poco probable
- 1: Muy Baja - Casi imposible

**IMPACTO FINANCIERO (1-5):**
- 5: Catastrófico - Multas/pérdidas >500.000€ o >10% facturación
- 4: Muy Alto - Multas/pérdidas 100.000€ - 500.000€
- 3: Alto - Multas/pérdidas 20.000€ - 100.000€
- 2: Medio - Multas/pérdidas 5.000€ - 20.000€
- 1: Bajo - Multas/pérdidas <5.000€

**IMPACTO REPUTACIONAL (1-5):**
- 5: Catastrófico - Crisis reputacional severa, cobertura mediática nacional
- 4: Muy Alto - Daño significativo a la marca
- 3: Alto - Afectación moderada a la reputación
- 2: Medio - Daño menor y recuperable
- 1: Bajo - Sin impacto reputacional

**IMPACTO OPERACIONAL (1-5):**
- 5: Catastrófico - Cierre de operaciones, pérdida de licencias
- 4: Muy Alto - Interrupción prolongada (>1 mes)
- 3: Alto - Interrupción temporal (1-4 semanas)
- 2: Medio - Afectación menor (<1 semana)
- 1: Bajo - Sin impacto operacional

**NIVEL DE RIESGO = Probabilidad x [(Imp. Financiero + Imp. Reputacional + Imp. Operacional) / 3]**

**INTERPRETACIÓN:**
- 20-25: CRÍTICO - Acción inmediata obligatoria
- 12-19: ALTO - Requiere atención prioritaria
- 6-11: MEDIO - Monitoreo y controles periódicos
- 3-5: BAJO - Revisión ocasional
- 0-2: TRIVIAL - Aceptable, sin acción requerida

Para cada riesgo, evalúa y responde en JSON:

```json
{{
  "riesgos_evaluados": [
    {{
      "id_riesgo": "RL-001",
      "categoria": "CONTRACTUAL",
      "descripcion": "Descripción del riesgo",
      "fuente_documento": "Fuente",
      "probabilidad_ocurrencia": 4,
      "impacto_financiero": 4,
      "impacto_reputacional": 3,
      "impacto_operacional": 2,
      "nivel_riesgo_calculado": 12.0,
      "nivel_riesgo": "Alto",
      "normativa_aplicable": ["Ley X"],
      "clausulas_relevantes": ["Cláusula Y"],
      "controles_actuales": ["Control existente"],
      "acciones_mitigacion": ["Acción 1", "Acción 2"],
      "responsable_sugerido": "Director Legal / Compliance Officer",
      "prioridad": "Alta",
      "metodologia": "RAM + Análisis Normativo"
    }}
  ]
}}
```

Evalúa cada riesgo con criterio jurídico profesional.
"""
