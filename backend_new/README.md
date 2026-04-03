# Riesgo IA - Backend Multi-Agente

Sistema backend con arquitectura multi-agente (LangGraph) para generación automática de matrices de riesgos SST (GTC 45:2012 y RAM).

## 📋 Arquitectura

### Esquema Medallón (Bronze/Silver/Gold)
- **Bronze**: Datos crudos de ingesta (documentos, textos extraídos)
- **Silver**: Datos normalizados (catálogos, normativas, resultados intermedios de agentes)
- **Gold**: Datos finales del negocio (matrices GTC 45 y RAM listas para exportar)

### Sistema Multi-Agente (LangGraph)
Flujo de procesamiento a través de 6 nodos:

1. **Agent_Extractor**: Extrae texto estructurado del documento → Bronze
2. **Agent_Hazard_ID**: Identifica procesos, actividades, tareas y peligros → Silver
3. **Agent_Risk_Mapper**: Asocia peligros a riesgos y efectos posibles → Silver
4. **Agent_Control_Planner**: Propone controles según jerarquía GTC 45 → Silver
5. **Node_Calculator** (Determin\u00edstico): Calcula NR=NP×NC, cruza matriz RAM → Sin IA
6. **Node_Builder**: Construye matriz final → Gold

### Stack Tecnológico
- **FastAPI** (v1.0) + Pydantic v2
- **PostgreSQL** + SQLAlchemy 2.x + Alembic
- **LangChain + LangGraph** para orquestación de agentes
- **Celery + Redis** para procesamiento asíncrono
- **PyMuPDF, python-docx, openpyxl** para procesamiento de documentos

## 🏗️ Estructura del Proyecto

```
backend/
├── agents/                  # Agentes individuales del grafo
│   ├── agent_extractor.py
│   ├── agent_hazard_id.py
│   ├── agent_risk_mapper.py
│   ├── agent_control_planner.py
│   ├── node_calculator.py
│   └── node_builder.py
├── db/                      # Base de datos
│   ├── schemas/            # Esquemas Bronze/Silver/Gold
│   │   ├── bronze.py
│   │   ├── silver.py
│   │   └── gold.py
│   ├── session.py
│   └── init_schemas.sql
├── graphs/                  # LangGraph workflows
│   ├── gtc45_graph.py      # Grafo principal
│   └── state.py            # AgentState (Pydantic)
├── api/                     # FastAPI endpoints
│   └── v1/
│       ├── ingest.py       # POST /ingest, GET /tasks/{id}
│       ├── matrix.py        # GET /matrix/{id}, /export
│       └── sources.py       # POST /sources/update
├── services/               # Servicios auxiliares
├── tasks/                  # Celery tasks
│   ├── ingestion_tasks.py
│   └── update_tasks.py
├── core/                   # Configuración
│   ├── config.py
│   └── celery_app.py
├── alembic/                # Migraciones de DB
├── server.py               # FastAPI app principal
├── sources_config.yaml     # Configuración de fuentes
├── requirements.txt
├── Dockerfile
└── .env
```

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Docker y Docker Compose instalados
- Puerto 5432 (PostgreSQL), 6379 (Redis), 8001 (API) disponibles

### Paso 1: Configurar variables de entorno

Crear archivo `.env` en `/app/backend/`:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://riesgo_admin:riesgo_secure_2024@postgres:5432/riesgo_ia

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# AI/LLM
EMERGENT_LLM_KEY=sk-emergent-c6dBf0c1231Fd2aE78

# App
DEBUG=False
CORS_ORIGINS=*
```

### Paso 2: Levantar servicios con Docker Compose

Desde la raíz del proyecto (`/app/`):

```bash
docker-compose up --build
```

Esto levanta:
- **postgres**: Base de datos PostgreSQL con esquemas Bronze/Silver/Gold
- **redis**: Broker y backend de Celery
- **backend**: API FastAPI en `http://localhost:8001`
- **celery_worker**: Worker para procesamiento asíncrono
- **celery_beat**: Scheduler para tareas programadas

### Paso 3: Ejecutar migraciones (primera vez)

```bash
docker-compose exec backend alembic upgrade head
```

### Paso 4: Verificar servicios

```bash
# Health check de la API
curl http://localhost:8001/health

# Documentación interactiva
open http://localhost:8001/api/docs
```

## 📡 Endpoints Principales

### POST /api/v1/ingest
Ingesta un documento y lanza el grafo de agentes

```bash
curl -X POST "http://localhost:8001/api/v1/ingest" \
  -F "file=@documento.pdf" \
  -F "empresa=Constructora XYZ Ltda"

# Response
{
  "task_id": "abc-123-def",
  "status": "pending",
  "message": "Documento recibido. Procesamiento iniciado."
}
```

### GET /api/v1/tasks/{task_id}
Consulta estado de procesamiento

```bash
curl "http://localhost:8001/api/v1/tasks/abc-123-def"

# Response
{
  "task_id": "abc-123-def",
  "status": "processing",
  "progress": {"message": "Identificando peligros..."}
}
```

### GET /api/v1/matrix/{id}
Obtiene matriz generada

```bash
curl "http://localhost:8001/api/v1/matrix/{matriz_id}"
```

### GET /api/v1/matrix/{id}/export
Descarga Excel

```bash
curl "http://localhost:8001/api/v1/matrix/{matriz_id}/export" -o matriz.xlsx
```

### POST /api/v1/sources/update
Actualiza catálogos y normativas

```bash
curl -X POST "http://localhost:8001/api/v1/sources/update"
```

## 🗄️ Esquemas de Base de Datos

### Bronze Schema
- `documentos_raw`: Documentos subidos
- `textos_extraidos`: Texto extraído por Agent_Extractor

### Silver Schema
- `normativas_gtc45`: Normativas oficiales
- `catalogo_peligros`: Catálogo de peligros
- `catalogo_controles`: Catálogo de controles SST
- `peligros_identificados`: Peligros detectados (Agent_Hazard_ID)
- `riesgos_mapeados`: Riesgos asociados (Agent_Risk_Mapper)
- `controles_planificados`: Controles propuestos (Agent_Control_Planner)

### Gold Schema
- `matrices_gtc45`: Matrices finales GTC 45
- `matrices_ram`: Matrices RAM (opcional)
- `exportaciones`: Registro de archivos generados

## 🔄 Pipeline de Fuentes (Actualización Automática)

Configurado en `sources_config.yaml`. Tareas programadas con Celery Beat:

- **update_normativas**: 2 AM el día 1 de cada mes
- **update_catalogos**: 3 AM todos los domingos
- **learn_from_matrices**: 1 AM todos los días

## 🧪 Testing

```bash
# Ejecutar tests
docker-compose exec backend pytest

# Con cobertura
docker-compose exec backend pytest --cov=. --cov-report=html
```

## 🔍 Monitoreo

### Celery Flower (opcional)
```bash
docker-compose exec celery_worker celery -A core.celery_app flower
# Abrir http://localhost:5555
```

### Logs
```bash
# Backend API
docker-compose logs -f backend

# Celery Worker
docker-compose logs -f celery_worker

# PostgreSQL
docker-compose logs -f postgres
```

## 📦 Dependencias Principales

```
fastapi==0.110.1
SQLAlchemy==2.0.29
celery==5.3.6
langchain==0.1.20
langgraph==0.0.55
psycopg2-binary==2.9.9
redis==5.0.3
PyMuPDF==1.24.2
python-docx==1.1.0
openpyxl==3.1.2
```

## 🛠️ Desarrollo

### Añadir nuevas migraciones
```bash
docker-compose exec backend alembic revision --autogenerate -m "descripcion"
docker-compose exec backend alembic upgrade head
```

### Acceder a PostgreSQL
```bash
docker-compose exec postgres psql -U riesgo_admin -d riesgo_ia

# Consultar esquemas
\dn

# Ver tablas de un esquema
\dt bronze.*
\dt silver.*
\dt gold.*
```

### Acceder a Redis CLI
```bash
docker-compose exec redis redis-cli

# Ver tareas en cola
KEYS celery*
```

## 🎯 Próximos Pasos (Fase 2)

1. Implementar lógica completa de cada agente
2. Integrar LLMs para análisis contextual
3. Generador de Excel con formato GTC 45 completo
4. Sistema de plantillas personalizables
5. API de edición inline de matrices
6. Dashboard avanzado con métricas
7. Pipeline de actualización automática funcional

## 📄 Licencia

Propietario - Riesgo IA © 2024

---

**Arquitectura**: Multi-Agente con LangGraph + Medallón (Bronze/Silver/Gold)  
**Stack**: FastAPI + PostgreSQL + Celery + Redis + LangChain  
**Versión**: 1.0.0 (Fase 1 - Infraestructura base)
