# 📦 Sistema de Pipeline de Ingesta Automática

## 🎯 Descripción General

El sistema de pipeline permite configurar fuentes de datos externas para **descargar automáticamente documentos** de forma periódica y procesarlos con el sistema de matrices SST.

## 🏗️ Arquitectura

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                   PIPELINE SYSTEM                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Scheduler  │──────│   Manager    │               │
│  │ (APScheduler)│      │              │               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                        │
│                               │                        │
│          ┌────────────────────┴────────────┐          │
│          ▼                    ▼             ▼          │
│   ┌────────────┐      ┌────────────┐  ┌────────────┐ │
│   │  Source 1  │      │  Source 2  │  │  Source N  │ │
│   │ (API/FTP)  │      │ (SharePnt) │  │  (Custom)  │ │
│   └─────┬──────┘      └─────┬──────┘  └─────┬──────┘ │
│         │                   │               │         │
│         └───────────────────┴───────────────┘         │
│                         ▼                              │
│                  ┌─────────────┐                      │
│                  │   Storage   │                      │
│                  │  (pending/  │                      │
│                  │  processed) │                      │
│                  └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### Directorios

```
/app/backend/services/pipeline/
├── __init__.py           # Exports principales
├── base.py               # Clase abstracta DataSource
├── manager.py            # PipelineManager (coordina todo)
├── scheduler.py          # Scheduler (cron jobs)
├── storage.py            # Almacenamiento de archivos
└── sources/              # Implementaciones de fuentes
    ├── __init__.py
    └── example_source.py # Plantilla de ejemplo
```

## 📝 Configuración

### Archivo: `/app/backend/config/pipeline_config.yaml`

```yaml
pipeline:
  enabled: true
  auto_process: true

storage:
  base_path: "/app/data/pipeline_ingestion"

sources:
  mi_fuente_1:
    enabled: true
    display_name: "Mi Fuente de Datos 1"
    type: "example"
    schedule: "0 9 * * 1"  # Lunes 9:00 AM
    config:
      url: "https://ejemplo.com/api/docs"
      # Agregar credenciales según la fuente
```

### Expresiones Cron

```
Formato: minuto hora día mes día_semana

Ejemplos:
"0 9 * * 1"      → Lunes a las 9:00 AM
"0 14 * * *"     → Todos los días a las 2:00 PM
"0 0 1 * *"      → Primer día de cada mes a medianoche
"0 */6 * * *"    → Cada 6 horas
"30 8 * * 1-5"   → Lunes a Viernes a las 8:30 AM
```

## 🔌 Crear una Nueva Fuente de Datos

### 1. Crear clase heredando de `DataSource`

```python
# /app/backend/services/pipeline/sources/mi_fuente.py

from typing import List, Dict, Any
from ..base import DataSource
import httpx

class MiFuenteCustom(DataSource):
    """
    Fuente de datos para [DESCRIPCIÓN]
    
    Configuración esperada:
    {
        'api_url': str,
        'api_key': str,
        'filters': dict  # Opcional
    }
    """
    
    def validate_config(self) -> bool:
        """Valida campos requeridos"""
        required = ['api_url', 'api_key']
        return all(field in self.config for field in required)
    
    async def fetch_documents(self) -> List[tuple[str, bytes]]:
        """
        Descarga documentos de la fuente.
        
        Returns:
            Lista de (nombre_archivo, contenido_bytes)
        """
        documents = []
        
        # Ejemplo: Conectar a API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.config['api_url'],
                headers={'Authorization': f"Bearer {self.config['api_key']}"}
            )
            
            # Procesar respuesta y descargar documentos
            data = response.json()
            for item in data['documents']:
                doc_response = await client.get(item['download_url'])
                documents.append((item['filename'], doc_response.content))
        
        return documents
```

### 2. Registrar en `sources/__init__.py`

```python
from .mi_fuente import MiFuenteCustom

__all__ = ['ExampleDataSource', 'MiFuenteCustom']
```

### 3. Agregar al config YAML

```yaml
sources:
  mi_fuente:
    enabled: true
    display_name: "Mi Fuente Custom"
    type: "custom"
    schedule: "0 9 * * *"
    config:
      api_url: "https://api.ejemplo.com/v1/docs"
      api_key: "tu_api_key_aqui"
```

### 4. Actualizar inicializador en `server.py`

```python
# En initialize_pipeline_system()
source_type = source_conf.get('type')

if source_type == 'custom':
    from services.pipeline.sources import MiFuenteCustom
    source = MiFuenteCustom(source_id, source_conf.get('config', {}))
elif source_type == 'example':
    source = ExampleDataSource(source_id, source_conf.get('config', {}))
```

## 🔄 API Endpoints

### 1. Estado del Sistema

```bash
GET /api/v1/pipeline/status
```

**Respuesta:**
```json
{
  "pipeline_enabled": true,
  "sources": [
    {
      "source_id": "example_1",
      "display_name": "Fuente Ejemplo",
      "enabled": true
    }
  ],
  "storage": {
    "pending": 5,
    "processed": 120,
    "failed": 2
  },
  "schedules": {
    "pipeline_example_1": {
      "source_id": "example_1",
      "cron": "0 9 * * 1",
      "next_run": "2025-01-13T09:00:00"
    }
  }
}
```

### 2. Ejecutar Pipeline Manualmente

```bash
POST /api/v1/pipeline/run
Content-Type: application/json

{
  "source_id": "example_1"  # Opcional, si es null ejecuta todas
}
```

### 3. Configurar Schedule

```bash
POST /api/v1/pipeline/schedule
Content-Type: application/json

{
  "source_id": "mi_fuente",
  "cron_expression": "0 14 * * *"
}
```

### 4. Ver Historial

```bash
GET /api/v1/pipeline/history?limit=20
```

### 5. Procesar Documentos Pendientes

```bash
POST /api/v1/pipeline/process-pending
```

## 📂 Sistema de Almacenamiento

### Estructura de Carpetas

```
/app/data/pipeline_ingestion/
├── pending/      # Documentos descargados pendientes de procesar
├── processed/    # Documentos procesados exitosamente
└── failed/       # Documentos que fallaron al procesarse
    └── *.error.txt  # Logs de error
```

### Flujo de Documentos

```
1. DESCARGA    → pending/
2. PROCESAR    → processed/  (éxito)
                 failed/      (error)
```

## 🔐 Seguridad

### Rate Limiting

Los endpoints de pipeline están protegidos por `slowapi`. Asegúrate de incluir `request: Request` en cada endpoint.

### Credenciales

**NUNCA** guardar credenciales en el código o en el repositorio. Usar:

1. Variables de entorno en `.env`
2. Secrets manager (producción)
3. Configuración YAML con referencias a env vars

```yaml
# ❌ INCORRECTO
config:
  api_key: "sk_live_12345"

# ✅ CORRECTO
config:
  api_key: "${API_KEY_MI_FUENTE}"  # Lee de variable de entorno
```

## 🧪 Testing

### Test Manual

```bash
# 1. Ejecutar pipeline
curl -X POST http://localhost:8001/api/v1/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"source_id": "example_1"}'

# 2. Ver estado
curl http://localhost:8001/api/v1/pipeline/status

# 3. Ver historial
curl http://localhost:8001/api/v1/pipeline/history
```

### Test Unitario

```python
import pytest
from services.pipeline import PipelineManager
from services.pipeline.sources import ExampleDataSource

@pytest.mark.asyncio
async def test_pipeline_ingestion():
    manager = PipelineManager()
    source = ExampleDataSource("test_source", {
        'url': 'https://test.com',
        'enabled': True
    })
    
    manager.register_source(source)
    results = await manager.run_ingestion("test_source")
    
    assert len(results) > 0
    assert results[0].success
```

## 📋 Checklist de Implementación

Cuando se definan las fuentes reales:

- [ ] Definir tipo de fuente (API, FTP, SharePoint, etc.)
- [ ] Implementar clase heredando de `DataSource`
- [ ] Validar configuración en `validate_config()`
- [ ] Implementar `fetch_documents()` con lógica de descarga
- [ ] Agregar manejo de errores y reintentos
- [ ] Configurar en `pipeline_config.yaml`
- [ ] Actualizar inicializador en `server.py`
- [ ] Probar manualmente con `/pipeline/run`
- [ ] Configurar schedule con cron
- [ ] Monitorear logs durante primera ejecución
- [ ] Integrar con SST Service para auto-procesamiento

## 🚀 Próximos Pasos

1. **Definir fuentes específicas**: Una vez conocidas las fuentes de datos (URLs, APIs, etc.)
2. **Implementar fuentes concretas**: Crear clases para cada fuente
3. **Configurar schedules**: Definir horarios de ejecución
4. **Auto-procesamiento**: Integrar con `SSTService` para procesar automáticamente documentos descargados
5. **Notificaciones**: Agregar alertas cuando falle una ingesta
6. **Dashboard**: Panel de control para monitorear pipelines

## 📚 Referencias

- [APScheduler Docs](https://apscheduler.readthedocs.io/)
- [Cron Expression](https://crontab.guru/)
- Arquitectura base: Clean Architecture + Service Layer Pattern
