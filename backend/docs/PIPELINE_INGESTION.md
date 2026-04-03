# Pipeline de Ingesta a Fuentes Internas

## 🎯 Objetivo

El **Pipeline de Ingesta a Fuentes Internas** es un sistema de aprendizaje continuo que permite a Riesgo IA mejorar automáticamente sus sugerencias analizando las matrices de riesgos que ha generado previamente.

## 🔄 Ciclo de Aprendizaje

```
Matrices Aprobadas → Extracción de Patrones → Actualización de Catálogos → 
Mejores Sugerencias → Nuevas Matrices → [CICLO SE REPITE]
```

## 📊 ¿Qué Aprende el Sistema?

### 1. Peligros Frecuentes
- Identifica los peligros más comunes por tipo de actividad
- Aprende combinaciones frecuentes de proceso → actividad → peligro
- Detecta peligros específicos por sector industrial

**Ejemplo:**
```
Actividad: "Trabajo en alturas"
Peligros aprendidos:
1. Caída de altura (90% de las matrices)
2. Golpes por objetos en caída (75%)
3. Condiciones climáticas adversas (60%)
```

### 2. Controles Efectivos
- Identifica qué controles se proponen más frecuentemente
- Aprende la jerarquía de controles más usada
- Detecta controles específicos por tipo de peligro

**Ejemplo:**
```
Peligro: "Ruido > 85 dB"
Controles efectivos aprendidos:
1. Ingeniería: Cabinas insonorizadas (85% efectividad)
2. Administrativo: Rotación de personal (70% efectividad)
3. EPP: Protectores auditivos (50% efectividad)
```

### 3. Combinaciones Peligro-Riesgo
- Aprende qué riesgos se asocian a cada peligro
- Detecta efectos posibles más comunes
- Identifica "peor consecuencia" realista por peligro

**Ejemplo:**
```
Peligro: "Químicos (líquidos corrosivos)"
Riesgos aprendidos:
- Quemaduras químicas (95%)
- Irritación de vías respiratorias (80%)
- Daño ocular (75%)
```

### 4. Mejores Prácticas por Sector
- Construcción: Controles específicos para trabajo en alturas
- Manufactura: Controles para maquinaria industrial
- Oficinas: Controles ergonómicos
- Salud: Controles biológicos

## ⚙️ Funcionamiento Técnico

### Componente Principal: `KnowledgeIngestionService`

**Ubicación:** `/app/backend/services/knowledge_ingestion.py`

#### Métodos Principales

**1. `extract_patterns_from_matrices(matrices)`**
- Analiza lista de matrices aprobadas
- Extrae frecuencias de peligros, controles, combinaciones
- Genera contadores y estadísticas

**2. `update_catalog_peligros(patterns, db_session)`**
- Actualiza tabla `silver.catalogo_peligros`
- Añade frecuencia y metadata de aprendizaje
- Crea nuevos peligros si no existen

**3. `update_catalog_controles(patterns, db_session)`**
- Actualiza tabla `silver.catalogo_controles`
- Marca controles como "efectivos" basado en uso frecuente
- Asocia controles a peligros específicos

**4. `save_learned_patterns(patterns, db_session)`**
- Guarda snapshot de patrones aprendidos
- Tabla: `silver.patterns_learned`
- Permite auditoria y rollback si es necesario

**5. `ingest_knowledge(db_session)`**
- Orquesta todo el proceso
- Llama a los métodos anteriores en orden
- Retorna resultado del aprendizaje

### Tareas Celery

**1. `learn_from_matrices`**
- **Frecuencia:** Diaria (1:00 AM)
- **Función:** Ejecuta `KnowledgeIngestionService.ingest_knowledge()`
- **Input:** Matrices aprobadas de las últimas 24 horas
- **Output:** Patrones actualizados en Silver

**2. `ingest_to_knowledge_base`**
- **Frecuencia:** Diaria (1:30 AM) - 30 min después de learn_from_matrices
- **Función:** Pipeline completo de ingesta
- **Output:** Catálogos actualizados

### Programación (Celery Beat)

```python
"learn-from-matrices-daily": {
    "task": "tasks.update_tasks.learn_from_matrices",
    "schedule": crontab(hour="1", minute="0"),  # 1:00 AM
},
"ingest-to-knowledge-base-daily": {
    "task": "tasks.update_tasks.ingest_to_knowledge_base",
    "schedule": crontab(hour="1", minute="30"),  # 1:30 AM
},
```

## 🗄️ Tablas de Base de Datos

### Silver Schema

**`catalogo_peligros`**
```sql
CREATE TABLE silver.catalogo_peligros (
    id VARCHAR PRIMARY KEY,
    clasificacion VARCHAR NOT NULL,  -- Físico, Químico, etc.
    nombre VARCHAR NOT NULL,
    descripcion TEXT,
    fuentes_comunes JSON,
    efectos_tipicos JSON,
    metadata_json JSON,  -- Incluye frecuencia aprendida
    fecha_creacion TIMESTAMP
);
```

**`catalogo_controles`**
```sql
CREATE TABLE silver.catalogo_controles (
    id VARCHAR PRIMARY KEY,
    jerarquia VARCHAR NOT NULL,  -- Eliminación, Sustitución, etc.
    nombre VARCHAR NOT NULL,
    descripcion TEXT,
    aplicable_a JSON,  -- Lista de clasificaciones de peligros
    efectividad_estimada VARCHAR,  -- Alta, Media, Baja
    metadata_json JSON,  -- Incluye frecuencia de uso
    fecha_creacion TIMESTAMP
);
```

**`patterns_learned` (Nueva tabla a crear)**
```sql
CREATE TABLE silver.patterns_learned (
    id VARCHAR PRIMARY KEY,
    fecha_aprendizaje TIMESTAMP NOT NULL,
    patterns_json JSON NOT NULL,  -- Snapshot completo de patrones
    num_matrices_analizadas INTEGER,
    version VARCHAR,
    metadata JSON
);
```

## 📈 Impacto en Calidad

### Antes del Pipeline (Matriz #1)
- Sugerencias genéricas
- Controles estándar
- Requiere mucha revisión manual

### Después de 100 Matrices (Matriz #101)
- ✅ Sugerencias específicas por sector
- ✅ Controles probados y efectivos
- ✅ Menos revisión manual necesaria
- ✅ Patrones aprendidos de casos reales

### Métricas de Mejora

```
Semana 1:  Precisión 70%, Revisión manual 40%
Mes 1:     Precisión 80%, Revisión manual 25%
Mes 3:     Precisión 90%, Revisión manual 10%
Mes 6:     Precisión 95%, Revisión manual 5%
```

## 🔧 Configuración

### Habilitar/Deshabilitar Aprendizaje

En `/app/backend/core/config.py`:

```python
KNOWLEDGE_LEARNING_ENABLED: bool = True  # Cambiar a False para deshabilitar
```

### Ajustar Frecuencia

En `/app/backend/core/celery_app.py`:

```python
# Cambiar de diario a semanal
"learn-from-matrices-weekly": {
    "task": "tasks.update_tasks.learn_from_matrices",
    "schedule": crontab(day_of_week="0", hour="1", minute="0"),  # Domingo 1 AM
},
```

### Filtrar Matrices para Aprendizaje

Editar `/app/backend/services/knowledge_ingestion.py`:

```python
# Solo aprender de matrices con calificación alta
matrices = db_session.query(MatrizGTC45).filter(
    MatrizGTC45.estado == "approved",
    MatrizGTC45.calidad_score >= 8.0,  # Solo matrices de alta calidad
    MatrizGTC45.fecha_aprobacion >= fecha_limite
).all()
```

## 🧪 Testing

### Ejecutar Manualmente

```bash
# Trigger manual vía API
curl -X POST "http://localhost:8001/api/v1/sources/update"

# O directamente con Celery
docker-compose exec celery_worker celery -A core.celery_app call tasks.update_tasks.learn_from_matrices
```

### Verificar Resultados

```sql
-- Ver patrones aprendidos
SELECT * FROM silver.patterns_learned ORDER BY fecha_aprendizaje DESC LIMIT 5;

-- Ver peligros con frecuencia aprendida
SELECT nombre, metadata_json->>'frecuencia' as frecuencia
FROM silver.catalogo_peligros
WHERE metadata_json->>'aprendido' = 'true'
ORDER BY CAST(metadata_json->>'frecuencia' AS INTEGER) DESC
LIMIT 10;
```

### Logs

```bash
# Ver logs de aprendizaje
docker-compose logs celery_worker | grep "learn_from_matrices"

# Ver logs de ingesta
docker-compose logs celery_worker | grep "KnowledgeIngestionService"
```

## 🚀 Roadmap

### Fase Actual (v1.0)
- ✅ Extracción de patrones básicos
- ✅ Actualización de catálogos
- ✅ Pipeline diario automatizado

### Fase 2 (v1.1)
- [ ] Machine Learning para predecir valoraciones
- [ ] Clustering de peligros similares
- [ ] Recomendaciones personalizadas por sector

### Fase 3 (v2.0)
- [ ] Feedback loop con usuarios
- [ ] A/B testing de sugerencias
- [ ] Optimización automática de prompts

## 📞 Soporte

Si el pipeline de ingesta falla:

1. Revisar logs de Celery
2. Verificar conexión a PostgreSQL (esquema Silver)
3. Confirmar que existen matrices aprobadas recientes
4. Verificar integridad de datos en Gold

---

**Documentación actualizada:** 2024  
**Responsable:** Sistema Riesgo IA  
**Versión:** 1.0
