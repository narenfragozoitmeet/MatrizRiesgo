# 🏗️ Estructura del Proyecto - Backend Riesgo IA

## 📁 Organización de Carpetas

```
backend_new/
├── 📋 prompts/                       # Prompts de cada agente (fácil modificación)
│   ├── agent_01_extractor_prompt.py
│   ├── agent_02_hazard_identifier_prompt.py
│   ├── agent_03_risk_mapper_prompt.py
│   └── agent_04_control_planner_prompt.py
│
├── 🎯 agents/                        # Agentes individuales (nomenclatura descriptiva)
│   ├── agent_01_extractor.py        # Extrae texto de documentos
│   ├── agent_02_hazard_identifier.py # Identifica peligros GTC 45
│   ├── agent_03_risk_mapper.py      # Mapea riesgos y efectos
│   ├── agent_04_control_planner.py  # Planifica controles (jerarquía)
│   ├── node_05_calculator.py        # Cálculos determin\u00edsticos (NO IA)
│   └── node_06_builder.py           # Construye matriz final → Gold
│
├── 📊 types/                         # Modelos Pydantic organizados por capa
│   ├── base_types.py                # Tipos fundamentales (Enums, Document)
│   ├── bronze_types.py              # Modelos para esquema Bronze
│   ├── silver_types.py              # Modelos para esquema Silver
│   └── gold_types.py                # Modelos para esquema Gold
│
├── 🔄 graphs/                        # LangGraph workflows
│   ├── state.py                     # AgentState (estado compartido)
│   └── gtc45_graph.py               # Grafo principal de 6 nodos
│
├── 🗄️ db/                            # Base de datos
│   ├── schemas/
│   │   ├── bronze.py                # Tablas Bronze (datos crudos)
│   │   ├── silver.py                # Tablas Silver (datos procesados)
│   │   └── gold.py                  # Tablas Gold (matrices finales)
│   ├── session.py                   # Configuración SQLAlchemy
│   └── init_schemas.sql             # Inicialización de esquemas
│
├── 🌐 api/                           # FastAPI endpoints
│   └── v1/
│       ├── ingest.py                # POST /ingest, GET /tasks/{id}
│       ├── matrix.py                # GET /matrix/{id}, /export
│       └── sources.py               # POST /sources/update
│
├── ⚙️ services/                      # Servicios auxiliares
│   ├── document_parser.py           # Parser de PDF/Word/Excel
│   └── (otros servicios)
│
├── 📦 tasks/                         # Celery tasks
│   ├── ingestion_tasks.py           # Tarea principal de procesamiento
│   └── update_tasks.py              # Actualización de fuentes
│
├── 🔧 core/                          # Configuración
│   ├── config.py                    # Settings (Pydantic)
│   └── celery_app.py                # Config Celery + Beat
│
├── 🛠️ utils/                         # Utilidades compartidas
│
├── 🔄 alembic/                       # Migraciones de DB
│
├── 📄 Archivos principales
│   ├── server.py                    # FastAPI app
│   ├── sources_config.yaml          # Config de fuentes normativas
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── README.md
│   └── ARCHITECTURE.md
│
└── 🐳 docker-compose.yml             # En raíz /app/
```

## 🎨 Convenciones de Nomenclatura

### Agentes
- **Formato**: `agent_XX_nombre_descriptivo.py`
- **Ejemplo**: `agent_02_hazard_identifier.py`
- **Clase**: `AgentXXNombreDescriptivo`
- **Función nodo**: `agent_XX_nombre_node()`

### Prompts
- **Formato**: `agent_XX_nombre_prompt.py`
- **Variables**: `SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE`
- **Función**: `get_nombre_prompt()`

### Tipos
- **Por capa**: `bronze_types.py`, `silver_types.py`, `gold_types.py`
- **Base**: `base_types.py` (enums y modelos fundamentales)

## 🚀 Flujo de Datos

```
1️⃣ Ingesta → Bronze
   POST /api/v1/ingest
   ↓
   Celery Task iniciada
   ↓
   Agent_01_Extractor
   ↓
   Bronze: documentos_raw, textos_extraidos

2️⃣ Procesamiento → Silver
   Agent_02_Hazard_Identifier
   ↓
   Silver: peligros_identificados
   ↓
   Agent_03_Risk_Mapper
   ↓
   Silver: riesgos_mapeados
   ↓
   Agent_04_Control_Planner
   ↓
   Silver: controles_planificados

3️⃣ Cálculo (Determinístico)
   Node_05_Calculator
   ↓
   Fórmulas GTC 45 (sin IA)

4️⃣ Construcción → Gold
   Node_06_Builder
   ↓
   Gold: matrices_gtc45
   ↓
   Task SUCCESS → matriz_id

5️⃣ Consulta
   GET /api/v1/matrix/{id}
   GET /api/v1/matrix/{id}/export
```

## 📝 Modificar Prompts

### Ejemplo: Cambiar prompt del Agent 02

1. Abrir `/prompts/agent_02_hazard_identifier_prompt.py`
2. Editar `SYSTEM_PROMPT` con las instrucciones deseadas
3. Guardar (los cambios se aplican automáticamente)

```python
SYSTEM_PROMPT = """
Tu nueva instrucción aquí...
"""
```

**No necesitas tocar el código del agente**, solo el archivo de prompt.

## 🔧 Añadir Nuevo Agente

1. Crear prompt: `/prompts/agent_05_nombre_prompt.py`
2. Crear agente: `/agents/agent_05_nombre.py`
3. Añadir al grafo: `/graphs/gtc45_graph.py`

```python
# En gtc45_graph.py
from agents.agent_05_nombre import agent_05_nombre_node

workflow.add_node("nombre", agent_05_nombre_node)
workflow.add_edge("control_planner", "nombre")
workflow.add_edge("nombre", "calculate")
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Test específico de un agente
pytest tests/test_agent_02_hazard_identifier.py

# Con cobertura
pytest --cov=agents --cov-report=html
```

## 📦 Dependencias Principales

```
fastapi==0.110.1          # API REST
SQLAlchemy==2.0.29        # ORM
celery==5.3.6             # Tareas asíncronas
langchain==0.1.20         # Framework LLM
langgraph==0.0.55         # Grafos de agentes
psycopg2-binary==2.9.9    # PostgreSQL driver
redis==5.0.3              # Broker Celery
```

## 🔍 Monitoreo y Debugging

### Ver logs de un agente específico
```bash
docker-compose logs -f celery_worker | grep "Agent_02"
```

### Ver estado de una tarea
```bash
curl http://localhost:8001/api/v1/tasks/{task_id}
```

### Inspeccionar base de datos
```bash
docker-compose exec postgres psql -U riesgo_admin -d riesgo_ia

\dt silver.*  # Ver tablas Silver
SELECT * FROM silver.peligros_identificados LIMIT 5;
```

## 📚 Documentación Adicional

- `ARCHITECTURE.md` - Diagramas visuales de arquitectura
- `sources_config.yaml` - Configuración de fuentes normativas
- API Docs: `http://localhost:8001/api/docs`

---

**Versión**: 1.0.0 - Fase 1 (Infraestructura base completada)  
**Arquitectura**: Multi-Agente LangGraph + Medallón PostgreSQL  
**Última actualización**: 2024
