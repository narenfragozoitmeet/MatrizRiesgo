# README actualizado

# 🛡️ Sistema de Matriz de Riesgos SST

Sistema profesional para generación automática de Matrices de Riesgos según GTC 45 + RAM.

## 🔒 Seguridad

### Configuración de Producción

1. **Variables de Entorno:**
```bash
cp backend/.env.example backend/.env
# Editar con valores reales
```

2. **API Key:**
- Obtener de: https://app.emergentagent.com/profile
- NUNCA commitear al repositorio
- Rotar cada 90 días

3. **CORS:**
- Configurar dominios permitidos en `.env`
- NO usar `*` en producción

4. **MongoDB:**
```bash
# En producción usar autenticación
MONGO_URL="mongodb://user:pass@host:27017/?authSource=admin&ssl=true"
```

5. **Rate Limiting:**
- Por defecto: 5 requests/minuto
- Ajustar según necesidad en `.env`

## 🧪 Testing

```bash
cd backend

# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v

# Coverage
pytest --cov=. --cov-report=html
```

## 🚀 Deployment

### Docker

```bash
# Build
docker build -t riesgo-ia-backend:latest ./backend

# Run
docker run -p 8001:8001 \
  -e MONGO_URL=mongodb://host:27017 \
  -e EMERGENT_LLM_KEY=your-key \
  riesgo-ia-backend:latest
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

## 📊 Monitoreo

- Health check: `GET /api/health`
- Metrics: Prometheus format en `/metrics` (TODO)
- Logs: Structured JSON en stdout

## 🏗️ Arquitectura

```
backend/
├── core/domain/          # Lógica de negocio pura
├── core/application/     # Casos de uso
├── infrastructure/       # Implementaciones (DB, LLM, etc.)
├── api/                  # Endpoints REST
├── shared/               # Utilidades compartidas
└── tests/                # Tests por capa
```

## 📝 Contribución

1. Fork el proyecto
2. Crear branch: `git checkout -b feature/nueva-feature`
3. Commit: `git commit -m 'Add nueva feature'`
4. Push: `git push origin feature/nueva-feature`
5. Abrir Pull Request

### Code Style

```bash
# Format
black .
isort .

# Lint
flake8 .
```

## 📄 Licencia

[Tu Licencia]

## 🆘 Soporte

- Issues: GitHub Issues
- Email: support@ejemplo.com
