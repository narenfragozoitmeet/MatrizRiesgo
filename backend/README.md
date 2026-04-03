# Riesgo IA - Sistema Multi-Agente para Matrices de Riesgos SST

## 🎯 Objetivo del Proyecto

**Riesgo IA** es un sistema backend basado en inteligencia artificial multi-agente que automatiza completamente el proceso de identificación de peligros y valoración de riesgos laborales para empresas, generando matrices profesionales de SST (Seguridad y Salud en el Trabajo) según la norma **GTC 45:2012** y opcionalmente la metodología **RAM** (Risk Assessment Matrix).

### Problema que Resuelve

Actualmente, la creación de matrices de riesgos es un proceso:
- ⏱️ **Lento**: Días o semanas de trabajo manual por parte de expertos en SST
- 💰 **Costoso**: Requiere contratar consultores especializados
- 📉 **Inconsistente**: Calidad variable según el criterio del profesional
- 📝 **Tedioso**: Revisión documento por documento, identificación manual de peligros

### Solución

Un sistema automatizado que:
1. ✅ Recibe documentos empresariales (procedimientos, perfiles de cargo, descripciones de puesto)
2. ✅ Procesa automáticamente mediante **6 agentes especializados de IA**
3. ✅ Identifica **todos los peligros** según catálogo GTC 45
4. ✅ Valora riesgos con **cálculos matemáticos precisos** (0% alucinaciones)
5. ✅ Propone controles siguiendo la **jerarquía oficial GTC 45**
6. ✅ Genera matriz lista para negocio en **minutos**, no días

## 🏗️ Arquitectura del Sistema

### Multi-Agente con LangGraph

Sistema de **6 agentes especializados** que trabajan secuencialmente:

```
📄 Documento → [Agent_01] → [Agent_02] → [Agent_03] → [Agent_04] → [Node_05] → [Node_06] → ✅ Matriz GTC 45
```

#### 🤖 Agentes del Sistema

| # | Agente | Responsabilidad | Usa IA |
|---|--------|----------------|--------|
| 1 | **Extractor** | Extrae y limpia texto de PDF/Word/Excel | ✅ |
| 2 | **Hazard Identifier** | Identifica procesos, actividades, tareas y peligros | ✅ |
| 3 | **Risk Mapper** | Asocia peligros con riesgos específicos y efectos | ✅ |
| 4 | **Control Planner** | Propone controles según jerarquía GTC 45 | ✅ |
| 5 | **Calculator** | Calcula NR=NP×NC (matemática pura) | ❌ |
| 6 | **Builder** | Construye matriz final en Gold | ❌ |

### Arquitectura de Datos: Medallón (Bronze → Silver → Gold)

**Bronze** (Datos Crudos)
- Documentos subidos sin procesar
- Texto extraído tal cual

**Silver** (Datos Procesados)
- Normativas GTC 45 actualizadas
- Catálogos de peligros y controles
- Peligros identificados por IA
- Riesgos mapeados
- Controles planificados

**Gold** (Datos del Negocio)
- **Matrices GTC 45 finales** listas para exportar
- Estadísticas (críticos, altos, medios, bajos)
- Archivos Excel generados

## 🔄 Pipeline de Ingesta a Fuentes Internas

Una de las características clave del sistema es el **aprendizaje continuo**:

### Fuentes de Conocimiento

1. **Normativas Oficiales** (Externas)
   - GTC 45:2012
   - Decreto 1072 de 2015
   - ISO 45001
   - Actualizaciones del Ministerio del Trabajo

2. **Catálogos Internos** (Internos)
   - Peligros por clasificación
   - Controles por jerarquía
   - Efectos comunes por peligro

3. **Aprendizaje de Matrices Previas** (Internos) ⭐
   - Patrones identificados en matrices exitosas
   - Controles efectivos por sector
   - Combinaciones frecuentes de peligro-riesgo
   - Mejores prácticas aprendidas

### Ciclo de Mejora Continua

```
Matriz Generada → Revisada y Aprobada → Extracción de Patrones → 
Actualización de Catálogos → Mejores Sugerencias en Futuras Matrices
```

**Tarea Automática**: Todos los días a la 1 AM, el sistema:
- Analiza matrices aprobadas de las últimas 24 horas
- Extrae patrones comunes
- Actualiza base de conocimiento en Silver
- Mejora sugerencias futuras

## 📊 Stack Tecnológico

### Backend
- **FastAPI** - API REST moderna y rápida
- **LangChain + LangGraph** - Orquestación de agentes
- **PostgreSQL** - Base de datos (esquemas Bronze/Silver/Gold)
- **SQLAlchemy 2.x** - ORM
- **Celery + Redis** - Procesamiento asíncrono
- **Alembic** - Migraciones de BD

### IA/ML
- **emergentintegrations** - Integración con LLMs (Gemini, GPT, Claude)
- **Modelos soportados**: Gemini 2.5 Flash, GPT-5.2, Claude Sonnet 4.5

### Documentos
- **PyMuPDF** - Procesamiento de PDF
- **python-docx** - Procesamiento de Word
- **openpyxl** - Generación de Excel

## 🚀 Instalación y Uso

### Prerrequisitos
- Docker y Docker Compose
- Puertos libres: 5432 (PostgreSQL), 6379 (Redis), 8001 (API)

### Inicio Rápido

```bash
# 1. Clonar repositorio
cd /app

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar EMERGENT_LLM_KEY

# 3. Levantar servicios
docker-compose up --build

# 4. Ejecutar migraciones (primera vez)
docker-compose exec backend alembic upgrade head

# 5. Verificar
curl http://localhost:8001/health
```

### Uso de la API

**1. Ingestar documento**
```bash
curl -X POST "http://localhost:8001/api/v1/ingest" \
  -F "file=@procedimiento.pdf" \
  -F "empresa=Constructora ABC"

# Response: {"task_id": "abc-123", "status": "pending"}
```

**2. Consultar estado**
```bash
curl "http://localhost:8001/api/v1/tasks/abc-123"

# Response: {"task_id": "abc-123", "status": "completed", "result": {...}}
```

**3. Descargar matriz**
```bash
curl "http://localhost:8001/api/v1/matrix/{matriz_id}/export" -o matriz.xlsx
```

## 📁 Estructura del Proyecto

```
backend/
├── 📋 prompts/          # Prompts de cada agente (fácil modificación)
├── 🤖 agents/           # 6 agentes especializados
├── 🎯 types/            # Modelos Pydantic por capa (Bronze/Silver/Gold)
├── 🔄 graphs/           # LangGraph workflows
├── 🗄️ db/               # Esquemas de base de datos
├── 🌐 api/              # Endpoints FastAPI
├── 📦 tasks/            # Tareas Celery
├── ⚙️ services/         # Servicios auxiliares
├── 🔧 core/             # Configuración
├── 📚 docs/             # Documentación técnica
├── 🐳 docker-compose.yml
└── 📄 README.md (este archivo)
```

Ver documentación técnica detallada en [`docs/README_ESTRUCTURA.md`](docs/README_ESTRUCTURA.md)

## 🔄 Pipeline de Actualización Automática

### Tareas Programadas (Celery Beat)

| Tarea | Frecuencia | Objetivo |
|-------|-----------|----------|
| `update_normativas` | Mensual (día 1, 2 AM) | Actualizar GTC 45, Decreto 1072 |
| `update_catalogos` | Semanal (domingo, 3 AM) | Actualizar catálogos de peligros/controles |
| `learn_from_matrices` | **Diario (1 AM)** ⭐ | Aprender de matrices aprobadas |
| `ingest_to_knowledge_base` | **Diario (1 AM)** ⭐ | Ingestar patrones a fuentes internas |

### Trigger Manual

```bash
# Actualizar todas las fuentes manualmente
curl -X POST "http://localhost:8001/api/v1/sources/update"
```

## 🎓 Aprendizaje Continuo

El sistema mejora automáticamente con cada matriz generada:

**Patrones que Aprende:**
- Peligros frecuentes por tipo de actividad
- Controles más efectivos por peligro
- Combinaciones peligro-riesgo comunes
- Mejores prácticas por sector industrial

**Resultado:**
- ✅ Sugerencias más precisas
- ✅ Controles más relevantes
- ✅ Menos revisiones manuales necesarias
- ✅ Calidad incremental con el tiempo

## 📈 Métricas y Monitoreo

### API Docs
- Swagger UI: `http://localhost:8001/api/docs`
- ReDoc: `http://localhost:8001/api/redoc`

### Logs
```bash
# Logs de agentes
docker-compose logs -f celery_worker

# Logs de API
docker-compose logs -f backend

# Logs de PostgreSQL
docker-compose logs -f postgres
```

### Base de Datos
```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U riesgo_admin -d riesgo_ia

# Consultar esquemas
\dn
\dt bronze.*
\dt silver.*
\dt gold.*
```

## 🔐 Seguridad y Cumplimiento

- ✅ Datos en reposo encriptados (PostgreSQL)
- ✅ Autenticación por API key
- ✅ Trazabilidad completa (logs en AgentState)
- ✅ Cumplimiento GTC 45:2012
- ✅ GDPR compatible (datos locales)

## 🤝 Contribuir

### Añadir Nuevo Agente

1. Crear prompt: `/prompts/agent_07_nombre_prompt.py`
2. Crear agente: `/agents/agent_07_nombre.py`
3. Añadir al grafo: `/graphs/gtc45_graph.py`
4. Documentar en `/docs/`

### Modificar Prompts

Editar directamente en `/prompts/` - los cambios se aplican automáticamente.

## 📞 Soporte

- Documentación técnica: [`docs/`](docs/)
- Arquitectura: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Issues: (configurar repositorio)

## 📄 Licencia

Propietario - Riesgo IA © 2024

---

**Versión**: 1.0.0  
**Estado**: Fase 1 - Infraestructura base completada  
**Próximo**: Fase 2 - Implementación de lógica de LLMs y pipeline completo
