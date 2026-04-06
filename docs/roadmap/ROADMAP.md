# 🗺️ ROADMAP - Sistema Matriz de Riesgos SST

**Última actualización:** Enero 2025  
**Versión Actual:** 1.0.0  
**Score Calidad:** 8.5/10

---

## 📊 ESTADO ACTUAL

### ✅ Completado (v1.0.0)

- [x] Sistema funcional de generación de matrices SST
- [x] Integración con Gemini 2.5 Flash (emergentintegrations)
- [x] Extracción automática de empresa del documento
- [x] Metodologías GTC 45 + RAM implementadas
- [x] Exportación a Excel profesional
- [x] UI Neobrutalism responsive
- [x] Seguridad básica (rate limiting, validaciones)
- [x] Tests unitarios e integración (95% cobertura crítica)
- [x] CI/CD pipeline configurado
- [x] Logging estructurado
- [x] Docker multi-stage
- [x] Documentación de seguridad

---

## 🚨 ACCIÓN INMEDIATA (HOY)

### Prioridad: CRÍTICA

- [ ] **Rotar EMERGENT_LLM_KEY expuesta**
  - Ubicación: `backend/.env`
  - Acción: Generar nueva key en https://app.emergentagent.com/profile
  - Archivo: `docs/guides/SECURITY_CHECKLIST.md`
  
- [ ] **Verificar .gitignore aplicado**
  ```bash
  git status backend/.env  # No debe aparecer
  git rm --cached backend/.env  # Si está trackeado
  ```

- [ ] **Configurar MongoDB Authentication (Producción)**
  - Actual: Sin auth (solo desarrollo)
  - Target: Usuario/password + SSL
  - Archivo: `docs/guides/DATABASE_SETUP.md`

---

## 📅 CORTO PLAZO (1-2 Semanas)

### Prioridad: ALTA

#### 1. Testing E2E (3-4 días)
**Objetivo:** Cubrir flujos completos de usuario

**Tasks:**
- [ ] Instalar Playwright
- [ ] Test: Upload PDF → Generar matriz → Descargar Excel
- [ ] Test: Validación de archivos inválidos
- [ ] Test: Rate limiting en acción
- [ ] Test: Manejo de errores en UI

**Entregables:**
- `backend/tests/e2e/test_complete_flow.py`
- Cobertura E2E: 80%+

**Owner:** QA Lead / Backend Dev  
**Archivo:** `docs/guides/TESTING_GUIDE.md`

---

#### 2. Monitoreo & Observabilidad (2-3 días)
**Objetivo:** Visibilidad de sistema en producción

**Tasks:**
- [ ] Implementar Prometheus metrics
  - Counter: `matriz_generations_total`
  - Histogram: `llm_request_duration_seconds`
  - Gauge: `active_connections`
  
- [ ] Configurar Grafana dashboards
  - Panel: Requests por minuto
  - Panel: Latencia LLM
  - Panel: Errores 4xx/5xx
  
- [ ] Integrar Sentry para error tracking
  ```python
  import sentry_sdk
  sentry_sdk.init(dsn="...")
  ```

**Entregables:**
- `/backend/monitoring/prometheus.py`
- `/backend/monitoring/metrics.py`
- Grafana dashboard JSON

**Owner:** DevOps / SRE  
**Archivo:** `docs/guides/MONITORING_SETUP.md`

---

#### 3. Caching Layer (2 días)
**Objetivo:** Reducir latencia y costos de LLM

**Tasks:**
- [ ] Instalar Redis
- [ ] Implementar cache para `/matrices` (TTL: 5 min)
- [ ] Cache de resultados LLM (por hash de documento)
- [ ] Invalidación automática

**Arquitectura:**
```
Request → Check Cache → Hit? Return : Process + Cache → Return
```

**Entregables:**
- `backend/infrastructure/cache/redis_cache.py`
- Tests de cache

**Owner:** Backend Dev  
**Estimación:** 16 horas

---

#### 4. Alertas & Notifications (1-2 días)
**Objetivo:** Respuesta rápida a incidentes

**Tasks:**
- [ ] Configurar alertas en Sentry
  - Error rate > 5%
  - Response time > 5s
  
- [ ] Email notifications para errores críticos
- [ ] Slack webhook para deploys

**Owner:** DevOps  
**Archivo:** `docs/guides/ALERTING_SETUP.md`

---

## 📅 MEDIANO PLAZO (1 Mes)

### Prioridad: MEDIA

#### 5. Clean Architecture Completa (1-2 semanas)
**Objetivo:** Desacoplar capas para mejor mantenibilidad

**Estructura Target:**
```
backend/
├── core/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── matriz_sst.py
│   │   │   ├── peligro.py
│   │   │   └── riesgo.py
│   │   ├── value_objects/
│   │   │   ├── nivel_riesgo.py
│   │   │   └── clasificacion.py
│   │   └── interfaces/  # Ports
│   │       ├── i_matriz_repository.py
│   │       └── i_llm_service.py
│   │
│   └── application/
│       ├── use_cases/
│       │   ├── generate_matriz.py
│       │   ├── export_matriz.py
│       │   └── list_matrices.py
│       └── dto/
│
├── infrastructure/  # Adapters
│   ├── repositories/
│   ├── ai/
│   └── exporters/
│
└── api/  # Controllers
```

**Tasks:**
- [ ] Extraer lógica de negocio a `domain/entities`
- [ ] Crear interfaces (ports)
- [ ] Implementar use cases
- [ ] Migrar repositories a infrastructure
- [ ] Refactor APIs para usar use cases

**Owner:** Tech Lead  
**Estimación:** 60-80 horas  
**Archivo:** `docs/architecture/CLEAN_ARCHITECTURE.md`

---

#### 6. Performance Optimization (3-5 días)
**Objetivo:** Reducir latencia 50%

**Tasks:**
- [ ] Profile de código (cProfile)
- [ ] Optimizar queries MongoDB (índices)
- [ ] Implementar connection pooling
- [ ] Async processing para operaciones pesadas
- [ ] CDN para assets estáticos

**Métricas Target:**
- Response time /ingest: < 30s (actual: ~45s)
- Response time /matrices: < 200ms
- Time to First Byte: < 100ms

**Owner:** Performance Engineer  
**Archivo:** `docs/guides/PERFORMANCE_TUNING.md`

---

#### 7. Multi-tenancy (1 semana)
**Objetivo:** Soporte para múltiples organizaciones

**Tasks:**
- [ ] Añadir modelo `Organization`
- [ ] API Key por organización
- [ ] Aislamiento de datos por tenant
- [ ] Quotas y límites por organización

**Schema:**
```python
class Organization:
    id: str
    name: str
    api_key: str
    plan: str  # free, pro, enterprise
    quota_monthly: int
    usage_current: int
```

**Owner:** Backend Lead  
**Archivo:** `docs/architecture/MULTI_TENANCY.md`

---

## 📅 LARGO PLAZO (3 Meses)

### Prioridad: BAJA

#### 8. Microservices Architecture (Si escala lo requiere)
**Objetivo:** Separar responsabilidades

**Servicios Propuestos:**
```
matriz-api-gateway      # Kong/Nginx
├── document-service    # Upload & extraction
├── ai-service          # LLM processing
├── matrix-service      # Business logic
├── export-service      # Excel generation
└── notification-service # Emails, webhooks
```

**Tasks:**
- [ ] Evaluar necesidad (> 10K users)
- [ ] Diseñar comunicación (REST vs gRPC vs Event-driven)
- [ ] Implementar service discovery
- [ ] Message broker (RabbitMQ/Kafka)

**Owner:** Solutions Architect  
**Estimación:** 3 meses  
**Archivo:** `docs/architecture/MICROSERVICES_PROPOSAL.md`

---

#### 9. ML Pipeline para Mejorar Prompts (2-3 semanas)
**Objetivo:** Optimizar prompts automáticamente

**Tasks:**
- [ ] Recopilar feedback de usuarios sobre matrices
- [ ] Entrenar modelo de clasificación de calidad
- [ ] A/B testing de prompts
- [ ] Prompt versioning

**Arquitectura:**
```
User Feedback → Training Pipeline → New Prompt → A/B Test → Deploy
```

**Owner:** ML Engineer  
**Archivo:** `docs/guides/ML_PIPELINE.md`

---

#### 10. Mobile App (2-3 meses)
**Objetivo:** App nativa iOS/Android

**Tech Stack:**
- React Native
- Expo
- React Native Paper (UI)

**Features:**
- Upload desde cámara/galería
- Ver historial de matrices
- Notificaciones push
- Offline mode

**Owner:** Mobile Team  
**Archivo:** `docs/roadmap/MOBILE_APP.md`

---

## 🎯 OBJETIVOS POR CUATRIMESTRE

### Q1 2025 (Ene-Mar)
- [x] MVP Funcional (v1.0.0)
- [ ] Testing completo (95%+)
- [ ] Monitoreo en producción
- [ ] Optimización de performance

**KPI Target:**
- Usuarios: 100+
- Matrices generadas: 500+
- Uptime: 99.5%
- Response time P95: < 3s

---

### Q2 2025 (Abr-Jun)
- [ ] Clean Architecture implementada
- [ ] Multi-tenancy
- [ ] API v2 (versioning)
- [ ] Features premium

**KPI Target:**
- Usuarios: 500+
- Matrices generadas: 5K+
- Uptime: 99.9%
- Organizaciones: 20+

---

### Q3 2025 (Jul-Sep)
- [ ] Microservices (si necesario)
- [ ] ML Pipeline
- [ ] Internacionalización (i18n)
- [ ] Compliance (ISO 27001)

**KPI Target:**
- Usuarios: 2K+
- Matrices generadas: 20K+
- Países: 5+

---

### Q4 2025 (Oct-Dic)
- [ ] Mobile App Beta
- [ ] Integrations (Zapier, Make)
- [ ] API pública
- [ ] Marketplace de templates

**KPI Target:**
- Usuarios: 5K+
- Mobile users: 500+
- Partners: 10+

---

## 📊 MÉTRICAS DE ÉXITO

### Técnicas
- **Uptime:** 99.9%
- **Response Time P95:** < 2s
- **Error Rate:** < 0.1%
- **Test Coverage:** > 90%
- **Build Time:** < 5 min
- **Deploy Time:** < 10 min

### Negocio
- **MRR (Monthly Recurring Revenue):** Target basado en plan
- **Churn Rate:** < 5%
- **Customer Satisfaction:** > 4.5/5
- **Time to Value:** < 5 min (primera matriz)

### Producto
- **Feature Adoption:** > 60%
- **Daily Active Users:** > 30% de total
- **Matrices por usuario/mes:** > 5

---

## 🛠️ HERRAMIENTAS & STACK

### Actual (v1.0.0)
- **Backend:** Python 3.12, FastAPI, MongoDB
- **Frontend:** React 19, Tailwind CSS
- **AI:** Gemini 2.5 Flash (emergentintegrations)
- **Deploy:** Supervisor, Nginx
- **Testing:** Pytest

### Próximo (v2.0.0)
- **Monitoring:** Prometheus, Grafana, Sentry
- **Cache:** Redis
- **CI/CD:** GitHub Actions
- **Security:** OWASP compliance
- **Documentation:** OpenAPI 3.1, Swagger

### Futuro (v3.0.0)
- **Orchestration:** Kubernetes
- **Service Mesh:** Istio
- **Message Broker:** Kafka
- **Search:** Elasticsearch
- **ML:** TensorFlow/PyTorch

---

## 👥 EQUIPO RECOMENDADO

### MVP (Actual)
- 1x Full-stack Developer
- 1x DevOps Engineer (part-time)

### Growth Phase (Q2 2025)
- 2x Backend Developers
- 1x Frontend Developer
- 1x DevOps/SRE
- 1x QA Engineer
- 1x Product Manager

### Scale Phase (Q4 2025)
- 4x Backend Developers
- 2x Frontend Developers
- 2x Mobile Developers
- 2x DevOps/SRE
- 2x QA Engineers
- 1x ML Engineer
- 1x Solutions Architect
- 1x Product Manager
- 1x UX Designer

---

## 📝 PRÓXIMOS PASOS INMEDIATOS

1. **Hoy:**
   - [ ] Rotar API key
   - [ ] Revisar logs de producción
   - [ ] Configurar alertas básicas

2. **Esta Semana:**
   - [ ] Implementar E2E tests
   - [ ] Setup Prometheus + Grafana
   - [ ] Configurar Sentry

3. **Este Mes:**
   - [ ] Redis caching
   - [ ] Performance optimization
   - [ ] Documentación API completa

---

## 🔗 REFERENCIAS

- [Guía de Seguridad](./guides/SECURITY_CHECKLIST.md)
- [Guía de Testing](./guides/TESTING_GUIDE.md)
- [Guía de Deployment](./guides/DEPLOYMENT_GUIDE.md)
- [Arquitectura Propuesta](./architecture/CLEAN_ARCHITECTURE.md)
- [Contribución](./guides/CONTRIBUTING.md)

---

**Última revisión:** Enero 2025  
**Próxima revisión:** Febrero 2025  
**Owner:** Tech Lead
