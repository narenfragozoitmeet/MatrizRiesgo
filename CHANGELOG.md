# 📝 CHANGELOG

## [1.1.1] - 2026-04-07

### ✨ Mejoras de Validación y UX

#### Backend - Validación de Archivos
- **Cambio crítico**: Límite de archivo aumentado de 10MB a **100MB**
- **Eliminada validación innecesaria**: Ya no se requiere "mínimo 100 caracteres"
- **Nueva validación**: Solo se verifica que el documento no esté completamente vacío
- **Actualizado**: `core/config.py` - `MAX_FILE_SIZE_MB: 100`
- **Actualizado**: `shared/validators.py` - Eliminada restricción de 100 caracteres

#### Frontend - Títulos y UX
- **Títulos limpios**: Cambio de mayúsculas forzadas a capitalización normal
  - "MATRIZ DE RIESGOS SST" → "Matriz de Riesgos SST"
  - "HISTORIAL DE MATRICES SST" → "Historial de Matrices SST"
  - "MATRIZ SST (GTC 45)" → "Matriz SST (GTC 45)"
  
- **Features mejoradas**: Títulos más simples con descripciones completas
  - **01 - Análisis Automático**: Descripción detallada sobre identificación con IA
  - **02 - Metodología**: Explicación completa de GTC 45 y RAM
  - **03 - Descarga en Excel**: Detalles del formato y contenido

- **Validación en frontend**: 
  - Verificación de tamaño de archivo (100 MB máximo)
  - Mensaje de error claro con tamaño del archivo
  - Tipos de archivo permitidos especificados

### 🐛 Correcciones
- Validación de texto ahora solo verifica que no esté vacío (no caracteres mínimos)
- Mensajes de error más claros y específicos

---

## [1.1.0] - 2026-04-06

### ✨ Agregado

#### Frontend - Mejora de UX/Copywriting
- **Textos más claros y concisos** en toda la interfaz
  - HomePage: Descripción principal más directa
  - Zona de upload: Texto simplificado
  - Pasos del proceso: Descripciones más cortas
  - Features: Títulos y descripciones optimizados
  - AnalysisPage: Mensajes más concisos
  - HistoryPage: Textos sin redundancias

#### Backend - Sistema de Pipeline de Ingesta Automática 🚀
- **Arquitectura abstracta y extensible** para fuentes de datos externas
- **Componentes principales:**
  - `DataSource` (clase abstracta): Interface para implementar fuentes personalizadas
  - `PipelineManager`: Gestor central de todos los pipelines
  - `PipelineScheduler`: Scheduler con soporte para expresiones cron
  - `PipelineStorage`: Sistema de almacenamiento (pending/processed/failed)

- **Nuevos Endpoints API:**
  - `GET /api/v1/pipeline/status` - Estado del sistema
  - `GET /api/v1/pipeline/sources` - Listar fuentes registradas
  - `GET /api/v1/pipeline/history` - Historial de ejecuciones
  - `POST /api/v1/pipeline/run` - Ejecutar pipeline manualmente
  - `POST /api/v1/pipeline/schedule` - Configurar horarios
  - `DELETE /api/v1/pipeline/schedule/{job_id}` - Eliminar schedule
  - `POST /api/v1/pipeline/process-pending` - Procesar documentos pendientes

- **Configuración YAML:** `/app/backend/config/pipeline_config.yaml`
  - Define fuentes de datos
  - Configura horarios con cron expressions
  - Control de habilitación/deshabilitación por fuente

- **Estructura de directorios:**
  ```
  /app/backend/services/pipeline/
  ├── base.py              # Clases abstractas
  ├── manager.py           # Gestor principal
  ├── scheduler.py         # Scheduler con APScheduler
  ├── storage.py           # Almacenamiento de archivos
  └── sources/             # Implementaciones de fuentes
      └── example_source.py
  ```

- **Sistema de almacenamiento:**
  ```
  /app/data/pipeline_ingestion/
  ├── pending/      # Documentos descargados
  ├── processed/    # Documentos procesados
  └── failed/       # Documentos con error + logs
  ```

#### Documentación
- **Nueva guía completa:** `/app/docs/guides/PIPELINE_GUIDE.md`
  - Arquitectura del sistema
  - Cómo crear fuentes personalizadas
  - Configuración de schedules
  - API endpoints
  - Ejemplos de implementación
  - Testing y troubleshooting

- **Actualizado ROADMAP:** Agregado task de implementar fuentes reales
- **Actualizado README:** Índice con nueva guía de pipeline

### 🔧 Dependencias
- `apscheduler==3.11.2` - Scheduler para tareas periódicas
- `aiofiles==25.1.0` - Operaciones asíncronas de archivos
- `pyyaml==6.0.2` - Parser de configuración YAML

### 📋 Próximos Pasos
1. **Definir fuentes de datos específicas** (APIs, SharePoint, FTP, etc.)
2. **Implementar clases concretas** heredando de `DataSource`
3. **Configurar schedules** para cada fuente
4. **Integrar con SSTService** para auto-procesamiento de documentos
5. **Configurar notificaciones** en caso de fallos

---

## [1.0.0] - 2025-01-XX

### ✨ Versión Inicial
- Sistema funcional de generación de matrices SST
- Integración con Google Gemini 2.5 Flash
- Extracción automática de nombre de empresa
- Metodologías GTC 45 + RAM
- Exportación a Excel profesional
- Frontend Neobrutalism con React + Tailwind
- Backend FastAPI + MongoDB
- Rate limiting y validaciones de seguridad
- Tests unitarios e integración
- Documentación completa
