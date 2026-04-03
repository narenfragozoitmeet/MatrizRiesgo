# Arquitectura del Sistema Riesgo IA

## Diagrama de Flujo Multi-Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTA DE DOCUMENTO                      │
│                   POST /api/v1/ingest (FastAPI)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Celery Task  │
                    │   (Async)     │
                    └───────┬───────┘
                            │
                    ┌───────▼────────┐
                    │   LangGraph    │
                    │   StateGraph   │
                    └───────┬────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │         AgentState (Pydantic)         │
        │  - task_id, status, documento         │
        │  - texto_extraido, peligros, riesgos  │
        └───────────────────┬───────────────────┘
                            │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   FLUJO DE AGENTES                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                            │
                ┌───────────▼──────────┐
                │  Agent_Extractor     │ ───► [BRONZE Schema]
                │  - Extrae texto      │      • documentos_raw
                │  - Limpia contenido  │      • textos_extraidos
                └───────────┬──────────┘
                            │
                ┌───────────▼──────────┐
                │  Agent_Hazard_ID     │ ───► [SILVER Schema]
                │  - Identifica:       │      • peligros_identificados
                │    • Procesos        │      • normativas_gtc45
                │    • Actividades     │      • catalogo_peligros
                │    • Tareas          │
                │    • Peligros        │
                └───────────┬──────────┘
                            │
                ┌───────────▼──────────┐
                │  Agent_Risk_Mapper   │ ───► [SILVER Schema]
                │  - Asocia riesgos    │      • riesgos_mapeados
                │  - Efectos posibles  │
                │  - Peor consecuencia │
                └───────────┬──────────┘
                            │
            ┌───────────────▼───────────────┐
            │  Agent_Control_Planner        │ ───► [SILVER Schema]
            │  - Controles existentes       │      • controles_planificados
            │  - Controles propuestos       │      • catalogo_controles
            │  - Jerarquía GTC 45:          │
            │    1. Eliminación             │
            │    2. Sustitución             │
            │    3. Ingeniería              │
            │    4. Administrativos         │
            │    5. EPP                     │
            └───────────────┬───────────────┘
                            │
                ┌───────────▼──────────┐
                │  Node_Calculator     │
                │  (DETERMINÍSTICO)    │
                │  - NP = ND × NE      │
                │  - NR = NP × NC      │
                │  - Interpretación    │
                │  - Matriz RAM        │
                │  ❌ NO usa LLM       │
                └───────────┬──────────┘
                            │
                ┌───────────▼──────────┐
                │  Node_Builder        │ ───► [GOLD Schema]
                │  - Formatea matriz   │      • matrices_gtc45
                │  - Calcula stats     │      • matrices_ram
                │  - Guarda en Gold    │      • exportaciones
                │  - Retorna matriz_id │
                └───────────┬──────────┘
                            │
                    ┌───────▼────────┐
                    │   COMPLETED    │
                    │  Celery Task   │
                    │    SUCCESS     │
                    └────────────────┘
```

## Arquitectura de Datos: Medallón

```
┌─────────────────────────────────────────────────────────────────┐
│                         BRONZE LAYER                             │
│                         (Datos Crudos)                           │
├─────────────────────────────────────────────────────────────────┤
│  📄 documentos_raw                                               │
│     - id, filename, storage_path, empresa                       │
│  📝 textos_extraidos                                             │
│     - texto_crudo, texto_limpio, metadata                       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [Transformación y Normalización]
┌─────────────────────────────────────────────────────────────────┐
│                         SILVER LAYER                             │
│                    (Datos Normalizados)                          │
├─────────────────────────────────────────────────────────────────┤
│  📚 normativas_gtc45         │  🏷️  catalogo_peligros           │
│  🛡️  catalogo_controles      │  ⚠️  peligros_identificados      │
│  🎯 riesgos_mapeados         │  🔧 controles_planificados       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [Agregación y Business Logic]
┌─────────────────────────────────────────────────────────────────┐
│                          GOLD LAYER                              │
│                    (Datos del Negocio)                           │
├─────────────────────────────────────────────────────────────────┤
│  ✅ matrices_gtc45                                               │
│     - Matriz completa lista para negocio                        │
│     - Estadísticas: críticos, altos, medios, bajos             │
│     - Resumen ejecutivo                                         │
│  🔀 matrices_ram (opcional)                                      │
│  📊 exportaciones                                                │
│     - Archivos Excel generados                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                                │
│                   React + Tailwind CSS                           │
│                   (Swiss Brutalist Design)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                       BACKEND API                                │
│              FastAPI v1 (/api/v1/...)                            │
│  • POST /ingest      • GET /tasks/{id}                          │
│  • GET /matrix/{id}  • GET /matrix/{id}/export                  │
│  • POST /sources/update                                          │
└────────┬────────────────────────────┬────────────────────────────┘
         │                            │
         │                            ▼
         │                  ┌──────────────────┐
         │                  │   Celery Worker  │
         │                  │   + LangGraph    │
         │                  │   (Async Tasks)  │
         │                  └────────┬─────────┘
         │                           │
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│   PostgreSQL     │        │      Redis       │
│   (Medallón)     │        │  - Broker        │
│  • bronze.*      │        │  - Result Store  │
│  • silver.*      │        │  - Cache         │
│  • gold.*        │        └──────────────────┘
└──────────────────┘
```

## Configuración de Fuentes (sources_config.yaml)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE FUENTES                           │
└─────────────────────────────────────────────────────────────────┘

📥 NORMATIVAS                    🔄 ACTUALIZACIÓN
   • GTC 45 Oficial                  • Monthly (1st day, 2 AM)
   • Decreto 1072 SST                • Celery Beat Schedule
   • ISO 45001                       • Manual trigger: POST /sources/update
   ↓ [Download PDFs + Web Scraping]
   📊 → silver.normativas_gtc45

📚 CATÁLOGOS                    🔄 ACTUALIZACIÓN
   • Peligros Físicos                • Weekly (Sunday, 3 AM)
   • Peligros Químicos               • Local JSON files
   • Controles SST                   • API integrations
   ↓ [Load JSON + API calls]
   📊 → silver.catalogo_peligros
        silver.catalogo_controles

🧠 APRENDIZAJE                  🔄 ACTUALIZACIÓN
   • Matrices previas                • Daily (1 AM)
   • Patrones comunes                • Pattern extraction
   • Mejores prácticas               • Knowledge base update
   ↓ [ML/Analysis]
   📊 → silver.patterns_learned
```

## Celery Beat Schedule

```yaml
Tareas Programadas:
┌────────────────────┬──────────────────┬────────────────────┐
│ Tarea              │ Frecuencia       │ Objetivo           │
├────────────────────┼──────────────────┼────────────────────┤
│ update_normativas  │ 1er día, 2 AM    │ Silver.normativas  │
│ update_catalogos   │ Domingo, 3 AM    │ Silver.catalogos   │
│ learn_from_matrices│ Diario, 1 AM     │ Silver.patterns    │
└────────────────────┴──────────────────┴────────────────────┘
```

## Docker Compose Services

```
┌──────────────────────────────────────────────────────────┐
│  postgres:5432       PostgreSQL 15                       │
│  redis:6379          Redis 7 (Broker + Backend)         │
│  backend:8001        FastAPI Server                      │
│  celery_worker       Celery Worker (2 concurrent)        │
│  celery_beat         Celery Scheduler                    │
└──────────────────────────────────────────────────────────┘
```

---

**Fase 1 Completada**: Infraestructura, Arquitectura de Datos y Diseño del Flujo de Agentes  
**Próximo**: Fase 2 - Implementación de la lógica de cada agente y conexión con LLMs
