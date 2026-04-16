# 📁 Estructura del Proyecto - Simplificada

## 🎯 Arquitectura Limpia y Modular

```
/app/
├── backend/                    # Backend FastAPI
│   ├── agents/                 # 🤖 Agentes LangChain (CORE)
│   │   ├── base.py            # Clase abstracta BaseAgent
│   │   ├── extractor.py       # Extracción PDF/DOCX/XLSX
│   │   ├── analyzer.py        # Análisis de peligros (LLM)
│   │   ├── calculator.py      # Cálculo GTC 45 + RAM
│   │   └── chain.py           # Orquestador principal
│   │
│   ├── api/v1/                # 🌐 Endpoints REST
│   │   ├── auth_api.py        # Autenticación JWT
│   │   ├── sst_api.py         # Matrices SST
│   │   └── pipeline_api.py    # Pipeline ingesta
│   │
│   ├── core/                  # ⚙️ Configuración
│   │   ├── config.py          # Settings (env vars)
│   │   └── security.py        # JWT & Auth
│   │
│   ├── db/                    # 🗄️ Base de datos
│   │   └── mongodb.py         # Conexión MongoDB
│   │
│   ├── models/                # 📊 Esquemas Pydantic
│   │   ├── user.py            # Usuario & Auth
│   │   └── matrices.py        # Matrices SST
│   │
│   ├── services/              # 🔧 Servicios
│   │   ├── excel_generator.py # Export Excel
│   │   └── pipeline/          # Sistema ingesta automática
│   │
│   ├── shared/                # 🛠️ Utilidades
│   │   ├── exceptions.py      # Excepciones custom
│   │   └── validators.py      # Validadores
│   │
│   ├── tests/                 # 🧪 Testing
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── server.py              # 🚀 App FastAPI
│   └── requirements.txt
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── pages/             # Páginas principales
│   │   │   ├── HomePage.js
│   │   │   ├── AnalysisPage.js
│   │   │   └── HistoryPage.js
│   │   ├── components/ui/     # Shadcn components
│   │   └── App.js
│   └── package.json
│
└── docs/                      # 📚 Documentación
    ├── guides/
    │   ├── SECURITY_IMPLEMENTATION.md
    │   ├── PIPELINE_GUIDE.md
    │   └── TESTING_GUIDE.md
    └── architecture/
        └── BACKEND_SIMPLIFIED_PROPOSAL.md
```

---

## 🚀 Componentes Principales

### 1. Sistema de Agentes (LangChain)
```python
MatrizProcessingChain
  ↓
  ├─→ DocumentExtractorAgent  # PDF → Texto
  ├─→ HazardAnalyzerAgent     # Texto → Peligros (LLM)
  └─→ RiskCalculatorAgent     # Peligros → Riesgos (GTC 45)
```

### 2. API Endpoints

| Endpoint | Descripción |
|----------|-------------|
| `POST /api/v1/auth/register` | Registro de usuario |
| `POST /api/v1/auth/login` | Login (JWT) |
| `POST /api/v1/ingest` | Procesar documento → matriz |
| `GET /api/v1/matrices` | Listar matrices |
| `GET /api/v1/matrix/{id}/export` | Descargar Excel |
| `GET /api/v1/pipeline/status` | Estado pipeline ingesta |

### 3. Stack Tecnológico

**Backend:**
- FastAPI 0.110+
- LangChain 0.3.7
- MongoDB (pymongo)
- Gemini 2.5 Flash (via langchain-google-genai)
- JWT Auth (python-jose + passlib)

**Frontend:**
- React 19
- Tailwind CSS
- Shadcn/UI
- Axios

---

## 📦 Lo que SE ELIMINÓ (limpieza)

❌ **Archivos/carpetas eliminados:**
- `agents/agent_01_extractor.py` → duplicado
- `agents/agent_02_hazard_identifier.py` → duplicado
- `agents/node_05_calculator.py` → duplicado
- `prompts/` → integrado en agentes
- `services/document_extractor.py` → reemplazado por agents/extractor.py
- `services/matriz_sst_processor.py` → reemplazado por agents/chain.py
- `api/v1/ingest.py` → consolidado en sst_api.py
- `api/v1/matrix.py` → consolidado en sst_api.py
- `db/schemas/` → PostgreSQL no usado
- `graphs/` → LangGraph no usado
- `types/` → innecesario con MongoDB
- `tasks/` → Celery no implementado
- `core/celery_app.py` → no usado

**Resultado:**
- De **166 archivos** → **~80 archivos** ✅
- Código más limpio y mantenible
- Sin duplicación
- Solo lo esencial

---

## 🎯 Flujo de Procesamiento Simplificado

```
Usuario sube documento
         ↓
    sst_api.py
         ↓
MatrizProcessingChain
         ↓
  ┌──────┴──────┐
  ↓             ↓
Extractor → Analyzer → Calculator
  ↓             ↓         ↓
Texto      Peligros   Riesgos
         ↓
    MongoDB
         ↓
  Descarga Excel
```

---

## 🔥 Quick Start

```bash
# Backend
cd /app/backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend
cd /app/frontend
yarn install
yarn start
```

---

## 📈 Métricas

| Métrica | Valor |
|---------|-------|
| **Archivos totales** | ~80 |
| **Agentes LangChain** | 3 |
| **Endpoints API** | 8 |
| **Dependencias Python** | ~30 |
| **LOC Backend** | ~2,000 |
| **Complejidad** | Baja ✅ |

---

## 🛡️ Seguridad

✅ JWT Authentication  
✅ Password hashing (bcrypt)  
✅ Rate limiting  
✅ CORS configurado  
✅ Sin credenciales hardcodeadas  
✅ Dockerfile non-root  

---

## 📚 Documentación

- [Seguridad](docs/guides/SECURITY_IMPLEMENTATION.md)
- [Pipeline](docs/guides/PIPELINE_GUIDE.md)
- [Testing](docs/guides/TESTING_GUIDE.md)
- [Arquitectura](docs/architecture/BACKEND_SIMPLIFIED_PROPOSAL.md)

---

**Proyecto optimizado y listo para producción** ✨
