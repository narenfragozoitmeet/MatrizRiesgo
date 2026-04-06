# 🛡️ MATRIZ DE RIESGOS - Sistema Inteligente de Evaluación

Sistema completo para generación automática de **Matrices de Riesgos SST (GTC 45)** y **Matrices de Riesgos Legales** usando Inteligencia Artificial.

## 🎯 Características

### Tipos de Matrices

#### 1. **Matriz SST (GTC 45)** - Seguridad y Salud en el Trabajo
- ✅ Identificación de peligros según clasificación GTC 45:
  - Físicos (ruido, temperaturas, vibraciones, iluminación)
  - Químicos (gases, vapores, polvos, líquidos)
  - Biológicos (virus, bacterias, hongos)
  - Biomecánicos/Ergonómicos (posturas, movimientos repetitivos)
  - Psicosociales (estrés, carga mental, acoso)
  - Mecánicos, Eléctricos, Locativos, Tecnológicos, etc.

- ✅ Evaluación según metodología GTC 45:
  - **Nivel de Deficiencia (ND)**: 0-10
  - **Nivel de Exposición (NE)**: 1-4
  - **Nivel de Probabilidad (NP)**: ND x NE
  - **Nivel de Consecuencia (NC)**: 10, 25, 60, 100
  - **Nivel de Riesgo (NR)**: NP x NC
  - **Interpretación**: Crítico, Alto, Medio, Bajo

#### 2. **Matriz de Riesgos Legales**
- ✅ Identificación de riesgos en categorías:
  - Contractual
  - Cumplimiento Normativo
  - Laboral
  - Fiscal
  - Regulatorio
  - Propiedad Intelectual
  - Ambiental
  - Protección de Datos
  - Corporativo
  - Litigios

- ✅ Evaluación con metodología RAM:
  - **Probabilidad de Ocurrencia**: 1-5
  - **Impacto Financiero**: 1-5
  - **Impacto Reputacional**: 1-5
  - **Impacto Operacional**: 1-5
  - **Nivel de Riesgo**: Probabilidad x [(ImpFin + ImpRep + ImpOp) / 3]

### Funcionalidades

- 📤 **Upload de documentos**: PDF, Word (.docx), Excel (.xlsx)
- 🤖 **Procesamiento con IA**: Google Gemini 2.5 Flash
- 📊 **Análisis inteligente**: Extracción automática de peligros y riesgos
- 📋 **Evaluación metodológica**: GTC 45 para SST, RAM para Legal
- 📥 **Exportación a Excel**: Formato profesional con colores por nivel de riesgo
- 📜 **Historial completo**: Acceso a todas las matrices generadas
- 🎨 **UI Moderna**: Diseño Neobrutalism con Tailwind CSS

## 🏗️ Arquitectura

### Backend
```
Python 3.12
├── FastAPI (0.115+)
├── MongoDB (pymongo 4.10+)
├── LangChain (0.3+) + LangGraph (0.2+)
├── emergentintegrations (Gemini 2.5 Flash)
├── PyMuPDF (extracción PDF)
├── python-docx (extracción Word)
├── openpyxl (Excel I/O)
└── pydantic (validación de datos)
```

**Arquitectura de Agentes:**
```
Documento → Extractor de Texto → Identificador de Riesgos → Evaluador (GTC45/RAM) → Constructor de Matriz → Excel
```

**Base de Datos (MongoDB):**
- `documentos_bronze`: Documentos originales
- `analisis_silver`: Datos procesados
- `matrices_sst`: Matrices GTC 45 generadas
- `matrices_legales`: Matrices legales generadas

### Frontend
```
React 19
├── React Router v7
├── Tailwind CSS 3.4+
├── shadcn/ui (componentes)
├── Axios (HTTP client)
└── Lucide React (iconos)
```

## 📡 API Endpoints

### Base URL
```
http://localhost:8001/api/v1
```

### Endpoints Principales

#### 1. Generar Matriz
```http
POST /api/v1/ingest

Content-Type: multipart/form-data

Body:
- file: <archivo PDF/Word/Excel>
- empresa: <nombre de la empresa>
- tipo_matriz: "sst" | "legal"

Response 200:
{
  "success": true,
  "message": "Matriz SST generada exitosamente",
  "matriz_id": "uuid-de-la-matriz",
  "tipo_matriz": "sst"
}
```

#### 2. Obtener Matriz
```http
GET /api/v1/matrix/{tipo}/{matriz_id}

Params:
- tipo: "sst" | "legal"
- matriz_id: UUID de la matriz

Response 200:
{
  "id": "uuid",
  "tipo_matriz": "sst",
  "empresa": "Constructora ACME",
  "documento_origen": "informe_sst.pdf",
  "total_riesgos": 12,
  "riesgos_criticos": 2,
  "riesgos_altos": 4,
  "riesgos_medios": 5,
  "riesgos_bajos": 1,
  "created_at": "2025-01-15T10:30:00",
  "metodologia": "GTC 45 + RAM"
}
```

#### 3. Exportar a Excel
```http
GET /api/v1/matrix/{tipo}/{matriz_id}/export

Response: Archivo .xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
```

#### 4. Listar Matrices
```http
GET /api/v1/matrices?tipo=sst

Query params (opcional):
- tipo: "sst" | "legal" | null (todas)

Response 200: Array de matrices
```

## 🚀 Instalación y Ejecución

### Prerequisitos
- Python 3.12+
- Node.js 18+
- MongoDB 7.0+
- Yarn

### Backend

```bash
cd /app/backend

# Instalar dependencias
pip install -r requirements.txt

# Instalar emergentintegrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Configurar .env
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="riesgo_ia"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=sk-emergent-XXXXX
LLM_MODEL_PROVIDER="gemini"
LLM_MODEL_NAME="gemini-2.5-flash"
EOF

# Ejecutar
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
cd /app/frontend

# Instalar dependencias
yarn install

# Configurar .env
cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
EOF

# Ejecutar
yarn start
```

### Supervisor (Producción)

```bash
sudo supervisorctl restart all
```

## 🧪 Testing

### Backend - Ejemplo con cURL

```bash
# Health check
curl http://localhost:8001/api/health

# Generar matriz SST
curl -X POST http://localhost:8001/api/v1/ingest \
  -F "file=@/path/to/documento.pdf" \
  -F "empresa=Constructora ACME" \
  -F "tipo_matriz=sst"

# Listar matrices
curl http://localhost:8001/api/v1/matrices
```

### Frontend - Testing Manual

1. Navegar a `http://localhost:3000`
2. Seleccionar tipo de matriz (SST o Legal)
3. Arrastrar/seleccionar documento
4. Ingresar nombre de empresa
5. Click "GENERAR MATRIZ DE RIESGOS"
6. Esperar procesamiento (30-60 segundos)
7. Visualizar resultados
8. Descargar Excel

## 📝 Prompts de Agentes

### Agente SST

**System Message:**
```
Eres un experto en Seguridad y Salud en el Trabajo (SST) especializado en la metodología GTC 45...
```

**Identificación:**
- Analiza texto del documento
- Identifica peligros por clasificación GTC 45
- Extrae proceso, zona, actividad, efectos, fuente

**Evaluación:**
- Asigna Nivel de Deficiencia (ND)
- Asigna Nivel de Exposición (NE)
- Calcula Nivel de Probabilidad (NP = ND x NE)
- Asigna Nivel de Consecuencia (NC)
- Calcula Nivel de Riesgo (NR = NP x NC)
- Propone controles

### Agente Legal

**System Message:**
```
Eres un experto abogado corporativo especializado en identificación y valoración de riesgos legales...
```

**Identificación:**
- Analiza documentos legales/corporativos
- Identifica riesgos por categoría legal
- Extrae normativa aplicable, cláusulas, consecuencias

**Evaluación:**
- Asigna Probabilidad de Ocurrencia (1-5)
- Asigna Impacto Financiero (1-5)
- Asigna Impacto Reputacional (1-5)
- Asigna Impacto Operacional (1-5)
- Calcula Nivel de Riesgo
- Propone acciones de mitigación

## 📊 Formato de Excel

### Matriz SST
Columnas:
- ID
- Proceso
- Zona/Lugar
- Actividad
- Clasificación Peligro
- Descripción Peligro
- Efectos Posibles
- Controles Existentes
- ND, NE, NP, Probabilidad
- NC, NR, Nivel Riesgo
- Controles Propuestos
- Fuente

**Colores por nivel:**
- 🔴 Crítico: Rojo (#DC2626)
- 🟠 Alto: Naranja (#EA580C)
- 🟡 Medio: Amarillo (#EAB308)
- 🟢 Bajo: Verde (#16A34A)

### Matriz Legal
Columnas:
- ID
- Categoría
- Descripción
- Normativa Aplicable
- Cláusulas Relevantes
- Probabilidad, Impactos
- NR Calculado, Nivel Riesgo
- Controles Actuales
- Acciones Mitigación
- Responsable
- Fuente

## 🔑 Variables de Entorno

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=riesgo_ia
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-XXXXX
LLM_MODEL_PROVIDER=gemini
LLM_MODEL_NAME=gemini-2.5-flash
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🎨 UI/UX

- **Diseño**: Neobrutalism con Tailwind CSS
- **Colores principales**:
  - Azul primario: `#002FA7`
  - Negro: `#0A0A0A`
  - Gris: `#52525B`, `#71717A`
  - Rojo error: `#DC2626`
  - Verde éxito: `#16A34A`

- **Tipografía**:
  - Títulos: Cabinet Grotesk (bold, tracking-tighter)
  - Monospace: JetBrains Mono

- **Componentes**:
  - Bordes: 2px solid
  - Sin border-radius (estilo brutal)
  - Shadow: `shadow-brutal` en hover
  - Transiciones suaves

## 📦 Estructura de Archivos

```
/app
├── backend/
│   ├── server.py                    # FastAPI app principal
│   ├── api/v1/
│   │   └── unified_api.py           # Endpoints REST
│   ├── core/
│   │   └── config.py                # Configuración
│   ├── db/
│   │   └── mongodb.py               # Conexión MongoDB
│   ├── models/
│   │   └── matrices.py              # Modelos Pydantic
│   ├── services/
│   │   ├── llm_service.py           # Servicio LLM
│   │   ├── document_extractor.py   # Extracción texto
│   │   ├── matriz_sst_processor.py # Procesador SST
│   │   ├── matriz_legal_processor.py # Procesador Legal
│   │   └── excel_generator.py      # Generador Excel
│   ├── prompts/
│   │   ├── sst_prompts.py          # Prompts SST
│   │   └── legal_prompts.py        # Prompts Legal
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.js                   # Router principal
    │   ├── pages/
    │   │   ├── HomePage.js          # Upload y selección
    │   │   ├── AnalysisPage.js      # Resultados
    │   │   └── HistoryPage.js       # Historial
    │   └── components/ui/           # shadcn/ui
    ├── package.json
    └── tailwind.config.js
```

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Ver logs
tail -f /var/log/supervisor/backend.err.log

# Verificar MongoDB
sudo systemctl status mongodb

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de integración LLM
```bash
# Verificar EMERGENT_LLM_KEY en .env
cat /app/backend/.env | grep EMERGENT_LLM_KEY

# Test manual
python -c "from services.llm_service import llm_service; print('OK')"
```

### Frontend no conecta con Backend
```bash
# Verificar REACT_APP_BACKEND_URL
cat /app/frontend/.env

# Verificar CORS en backend
curl -i http://localhost:8001/api/health
```

## 📄 Licencia

Proyecto desarrollado para EMERGENT AI - 2025

## 👥 Soporte

Para soporte técnico o consultas, contactar al equipo de desarrollo.

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-15  
**Stack**: Python 3.12 + FastAPI + MongoDB + React 19 + Gemini 2.5 Flash
