# 🎯 Propuesta: Arquitectura Backend Simplificada y Modular

## 📋 Análisis del Proyecto Actual vs. Propuesta

### ❌ Complejidad Innecesaria a ELIMINAR

1. **PostgreSQL** → Mantener solo MongoDB (suficiente para este caso)
2. **Arquitectura Medallón (Bronze/Silver/Gold)** → Sobre-ingeniería para el alcance actual
3. **Celery + Redis** → Opcional, solo si procesamiento asíncrono es crítico
4. **Múltiples capas de abstracción** → Simplificar a lo esencial

### ✅ Mantener y Mejorar

1. **MongoDB** → Base de datos única y suficiente
2. **LangChain** → Para agentes y procesamiento con LLM
3. **FastAPI** → Framework actual
4. **Estructura modular** → Pero simplificada

---

## 🏗️ Arquitectura Backend Propuesta (Simplificada)

```
/app/backend/
├── api/
│   └── v1/
│       ├── auth.py          # Autenticación JWT
│       ├── matrices.py       # CRUD de matrices
│       └── processing.py     # Trigger de procesamiento
│
├── core/
│   ├── config.py            # Configuración
│   └── security.py          # JWT y auth
│
├── db/
│   └── mongodb.py           # Conexión MongoDB
│
├── agents/                   # ← NUEVO: Agentes LangChain
│   ├── __init__.py
│   ├── base.py              # Clase base de agentes
│   ├── extractor.py         # Agente: Extraer texto de documentos
│   ├── analyzer.py          # Agente: Analizar peligros con LLM
│   ├── calculator.py        # Agente: Calcular niveles de riesgo
│   └── chain.py             # Cadena LangChain que orquesta todo
│
├── services/
│   ├── document_service.py  # Lógica de documentos
│   └── matrix_service.py    # Lógica de matrices
│
├── models/
│   ├── user.py              # Esquemas de usuario
│   ├── matriz.py            # Esquemas de matriz
│   └── document.py          # Esquemas de documento
│
├── shared/
│   ├── exceptions.py        # Excepciones custom
│   └── validators.py        # Validadores
│
├── tests/                   # Tests unitarios
│   ├── test_agents.py
│   ├── test_services.py
│   └── test_api.py
│
└── server.py                # Aplicación FastAPI
```

---

## 🤖 Componente Clave: Agentes con LangChain

### Estructura de Agentes Propuesta

#### 1. **Base Agent** (`agents/base.py`)
```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain.schema import Document

class BaseAgent(ABC):
    \"\"\"Clase base para todos los agentes\"\"\"
    
    def __init__(self, llm=None):
        self.llm = llm
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Ejecuta la lógica del agente\"\"\"
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        \"\"\"Valida la entrada del agente\"\"\"
        pass
```

#### 2. **Extractor Agent** (`agents/extractor.py`)
```python
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
from .base import BaseAgent

class DocumentExtractorAgent(BaseAgent):
    \"\"\"Agente para extraer texto de documentos\"\"\"
    
    async def execute(self, input_data):
        file_path = input_data["file_path"]
        file_type = input_data["file_type"]
        
        # Usar LangChain loaders
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "docx":
            loader = Docx2txtLoader(file_path)
        
        documents = loader.load()
        text = "\\n".join([doc.page_content for doc in documents])
        
        return {
            "raw_text": text,
            "num_pages": len(documents),
            "source": file_path
        }
```

#### 3. **Analyzer Agent** (`agents/analyzer.py`)
```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class PeligroIdentificado(BaseModel):
    peligro: str = Field(description="Descripción del peligro")
    fuente: str = Field(description="Fuente de información")
    area: str = Field(description="Área afectada")
    tipo: str = Field(description="Tipo de peligro según GTC 45")

class HazardAnalyzerAgent(BaseAgent):
    \"\"\"Agente para identificar peligros con LLM\"\"\"
    
    async def execute(self, input_data):
        text = input_data["raw_text"]
        empresa = input_data.get("empresa", "Empresa")
        
        # Parser estructurado
        parser = PydanticOutputParser(pydantic_object=List[PeligroIdentificado])
        
        # Prompt template
        prompt = ChatPromptTemplate.from_template(
            \"\"\"Eres un experto en SST (Seguridad y Salud en el Trabajo).
            
            Analiza el siguiente documento de la empresa {empresa} e identifica 
            TODOS los peligros laborales mencionados según la metodología GTC 45.
            
            Documento:
            {text}
            
            {format_instructions}
            \"\"\"
        )
        
        # Cadena LangChain
        chain = prompt | self.llm | parser
        
        result = await chain.ainvoke({
            "empresa": empresa,
            "text": text[:15000],  # Limitar tokens
            "format_instructions": parser.get_format_instructions()
        })
        
        return {
            "peligros": [p.dict() for p in result],
            "total_peligros": len(result)
        }
```

#### 4. **Calculator Agent** (`agents/calculator.py`)
```python
class RiskCalculatorAgent(BaseAgent):
    \"\"\"Agente para calcular niveles de riesgo (GTC 45 + RAM)\"\"\"
    
    async def execute(self, input_data):
        peligros = input_data["peligros"]
        
        # Usar LLM para estimar ND, NE, NC
        prompt = ChatPromptTemplate.from_template(
            \"\"\"Dado el siguiente peligro, estima los valores según GTC 45:
            
            Peligro: {peligro}
            Área: {area}
            
            Asigna valores de:
            - ND (Nivel de Deficiencia): 2, 6, 10
            - NE (Nivel de Exposición): 1, 2, 3, 4
            - NC (Nivel de Consecuencia): 10, 25, 60, 100
            
            Responde SOLO con formato JSON:
            {{"ND": X, "NE": Y, "NC": Z, "justificacion": "..."}}
            \"\"\"
        )
        
        riesgos_calculados = []
        for peligro in peligros:
            # Llamar LLM para cada peligro
            response = await (prompt | self.llm).ainvoke(peligro)
            
            # Calcular nivel de riesgo
            nd = response["ND"]
            ne = response["NE"]
            nc = response["NC"]
            nr = nd * ne * nc
            
            # Clasificar
            if nr >= 4000: nivel = "Crítico"
            elif nr >= 600: nivel = "Alto"
            elif nr >= 150: nivel = "Medio"
            else: nivel = "Bajo"
            
            riesgos_calculados.append({
                **peligro,
                "ND": nd,
                "NE": ne,
                "NC": nc,
                "NR": nr,
                "nivel_riesgo": nivel
            })
        
        return {"riesgos": riesgos_calculados}
```

#### 5. **Processing Chain** (`agents/chain.py`)
```python
from langchain.schema.runnable import RunnableSequence

class MatrizProcessingChain:
    \"\"\"Cadena que orquesta todos los agentes\"\"\"
    
    def __init__(self, llm):
        self.extractor = DocumentExtractorAgent()
        self.analyzer = HazardAnalyzerAgent(llm)
        self.calculator = RiskCalculatorAgent(llm)
    
    async def process_document(self, file_path: str, file_type: str, empresa: str = None):
        \"\"\"Procesa documento completo\"\"\"
        
        # Paso 1: Extraer texto
        extraction_result = await self.extractor.execute({
            "file_path": file_path,
            "file_type": file_type
        })
        
        # Paso 2: Analizar peligros
        analysis_result = await self.analyzer.execute({
            "raw_text": extraction_result["raw_text"],
            "empresa": empresa or "Sin especificar"
        })
        
        # Paso 3: Calcular riesgos
        calculation_result = await self.calculator.execute({
            "peligros": analysis_result["peligros"]
        })
        
        return {
            "empresa": empresa,
            "documento_origen": file_path,
            "riesgos": calculation_result["riesgos"],
            "total_riesgos": len(calculation_result["riesgos"]),
            "metadata": {
                "num_pages": extraction_result["num_pages"],
                "total_peligros_identificados": analysis_result["total_peligros"]
            }
        }
```

---

## 🔄 Flujo Simplificado

```
┌─────────────────┐
│  Usuario sube   │
│    documento    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  API: POST /process     │
│  - Valida archivo       │
│  - Guarda temporalmente │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  MatrizProcessingChain          │
│  ┌─────────────────────┐        │
│  │ 1. ExtractorAgent   │        │
│  │    (PDF → Text)     │        │
│  └──────────┬──────────┘        │
│             ▼                    │
│  ┌─────────────────────┐        │
│  │ 2. AnalyzerAgent    │        │
│  │    (LLM identifica) │        │
│  │    peligros)        │        │
│  └──────────┬──────────┘        │
│             ▼                    │
│  ┌─────────────────────┐        │
│  │ 3. CalculatorAgent  │        │
│  │    (LLM estima +    │        │
│  │     cálculo NR)     │        │
│  └──────────┬──────────┘        │
└─────────────┼──────────────────┘
              ▼
   ┌──────────────────────┐
   │  Guardar en MongoDB  │
   │  - Matriz completa   │
   │  - Asociar a usuario │
   └──────────┬───────────┘
              ▼
   ┌──────────────────────┐
   │  Retornar matriz_id  │
   │  al frontend         │
   └──────────────────────┘
```

---

## 📦 Dependencias Mínimas

```txt
# Core
fastapi==0.110.1
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Database
pymongo==4.6.2
motor==3.3.2

# LangChain
langchain==0.3.0          # ← Versión moderna
langchain-community==0.3.0
langchain-google-genai    # ← Para Gemini

# Documentos
pypdf==4.0.0
python-docx==1.1.0
openpyxl==3.1.2

# Auth
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4

# Utilidades
pydantic==2.7.0
pydantic-settings==2.2.1
python-dotenv==1.0.1
```

---

## 🎯 Ventajas de esta Arquitectura

### ✅ Simplicidad
- Una sola base de datos (MongoDB)
- Sin capas innecesarias
- Código fácil de entender

### ✅ Modularidad
- Agentes independientes y reutilizables
- Fácil agregar nuevos agentes
- Testing simple (cada agente es testeable)

### ✅ Escalabilidad
- Si crece, puedes agregar Celery después
- LangChain ya preparado para más complejidad
- Fácil migrar agentes a microservicios

### ✅ Mantenibilidad
- Menos código = menos bugs
- Estructura clara y predecible
- Documentación simple

---

## 🔧 Comparación con Propuesta Original

| Aspecto | Propuesta Original | Propuesta Simplificada |
|---------|-------------------|------------------------|
| **Base de datos** | MongoDB + PostgreSQL | Solo MongoDB |
| **Arquitectura** | Medallón (Bronze/Silver/Gold) | Servicios + Agentes |
| **Async tasks** | Celery + Redis | Opcional (agregar si es necesario) |
| **Agentes** | LangGraph (complejo) | LangChain (simple y directo) |
| **Capas** | 5-6 capas | 3 capas (API → Agents → DB) |
| **Complejidad** | Alta | Media |
| **Tiempo desarrollo** | ~30 horas | ~10 horas |

---

## 📝 Recomendación Final

**Implementa esta arquitectura simplificada:**

1. **Fase 1** (2-3 horas): 
   - Estructura de agentes con LangChain
   - Agente extractor básico

2. **Fase 2** (3-4 horas):
   - Agente analyzer con LLM
   - Agente calculator

3. **Fase 3** (2-3 horas):
   - Integrar cadena completa
   - Testing básico

4. **Fase 4** (2-3 horas):
   - Export a Excel
   - Mejoras de UX

**Total: ~10-13 horas** vs. 30+ horas de la propuesta original.

---

## 🚀 Siguiente Paso

¿Quieres que implemente esta arquitectura simplificada con LangChain?

Comenzaría por:
1. Instalar dependencias actualizadas de LangChain
2. Crear estructura de agentes
3. Implementar cadena básica de procesamiento
4. Integrar con endpoints existentes

**¿Procedo con esta implementación simplificada?**
