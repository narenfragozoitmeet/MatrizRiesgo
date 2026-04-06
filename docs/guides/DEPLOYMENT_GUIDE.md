# 📦 DEPLOYMENT GUIDE

**Sistema:** Matriz de Riesgos SST  
**Environments:** Development, Staging, Production

---

## 🏗️ ARQUITECTURA DE DEPLOYMENT

```
┌─────────────────────────────────────────┐
│         Load Balancer / CDN             │
│         (Nginx / Cloudflare)            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼─────┐   ┌─────▼──────┐
│  Frontend  │   │  Backend   │
│  (React)   │   │  (FastAPI) │
│  Port 3000 │   │  Port 8001 │
└────────────┘   └─────┬──────┘
                       │
                 ┌─────▼──────┐
                 │  MongoDB   │
                 │  Port 27017│
                 └────────────┘
```

---

## 🌍 ENVIRONMENTS

### Development (Local)

```bash
# Backend
cd /app/backend
export ENVIRONMENT=development
export DEBUG=true
export MONGO_URL=mongodb://localhost:27017
uvicorn server:app --reload --port 8001

# Frontend
cd /app/frontend
export REACT_APP_BACKEND_URL=http://localhost:8001
npm start
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/api/docs

---

### Staging (Pre-producción)

**Propósito:** Testing final antes de producción

```bash
# Variables
ENVIRONMENT=staging
DEBUG=true  # Mantener docs
MONGO_URL=mongodb://staging-db:27017/riesgo_ia_staging
CORS_ORIGINS=https://staging.tu-dominio.com
```

**Deployment:**
```bash
# Docker Compose
docker-compose -f docker-compose.staging.yml up -d

# O Kubernetes
kubectl apply -f k8s/staging/
```

---

### Production

**Propósito:** Usuarios reales

```bash
# Variables (.env NO commitear)
ENVIRONMENT=production
DEBUG=false  # Ocultar /api/docs
MONGO_URL=mongodb://admin:PASS@prod-db:27017/?ssl=true&authSource=admin
CORS_ORIGINS=https://tu-dominio.com
EMERGENT_LLM_KEY=sk-emergent-PROD-KEY
MAX_FILE_SIZE_MB=10
RATE_LIMIT_PER_MINUTE=10
```

---

## 🐳 DOCKER DEPLOYMENT

### Build Images

```bash
# Backend
cd /app/backend
docker build -t riesgo-ia-backend:v1.0.0 .
docker tag riesgo-ia-backend:v1.0.0 riesgo-ia-backend:latest

# Frontend
cd /app/frontend
docker build -t riesgo-ia-frontend:v1.0.0 .
docker tag riesgo-ia-frontend:v1.0.0 riesgo-ia-frontend:latest

# Push to registry
docker push your-registry.com/riesgo-ia-backend:v1.0.0
docker push your-registry.com/riesgo-ia-frontend:v1.0.0
```

---

### Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: riesgo-mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
    volumes:
      - mongo-data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js
    networks:
      - riesgo-network
    ports:
      - "27017:27017"

  backend:
    image: riesgo-ia-backend:latest
    container_name: riesgo-backend
    restart: always
    depends_on:
      - mongodb
    environment:
      MONGO_URL: mongodb://admin:${MONGO_ROOT_PASSWORD}@mongodb:27017
      EMERGENT_LLM_KEY: ${EMERGENT_LLM_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS}
      ENVIRONMENT: production
      DEBUG: false
    networks:
      - riesgo-network
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: riesgo-ia-frontend:latest
    container_name: riesgo-frontend
    restart: always
    environment:
      REACT_APP_BACKEND_URL: https://api.tu-dominio.com
    networks:
      - riesgo-network
    ports:
      - "3000:3000"

  nginx:
    image: nginx:alpine
    container_name: riesgo-nginx
    restart: always
    depends_on:
      - backend
      - frontend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - riesgo-network
    ports:
      - "80:80"
      - "443:443"

volumes:
  mongo-data:

networks:
  riesgo-network:
    driver: bridge
```

**Deploy:**
```bash
# Cargar variables
export MONGO_ROOT_PASSWORD=strong_password_here
export EMERGENT_LLM_KEY=sk-emergent-your-key
export CORS_ORIGINS=https://tu-dominio.com

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

---

## ☸️ KUBERNETES DEPLOYMENT

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: riesgo-ia
```

---

### Secrets

```bash
# Crear secrets
kubectl create secret generic riesgo-secrets \
  --from-literal=mongo-password=STRONG_PASSWORD \
  --from-literal=emergent-llm-key=sk-emergent-KEY \
  -n riesgo-ia
```

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: riesgo-secrets
  namespace: riesgo-ia
type: Opaque
data:
  mongo-password: <base64-encoded>
  emergent-llm-key: <base64-encoded>
```

---

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: riesgo-config
  namespace: riesgo-ia
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  MAX_FILE_SIZE_MB: "10"
  RATE_LIMIT_PER_MINUTE: "10"
  CORS_ORIGINS: "https://tu-dominio.com"
```

---

### MongoDB Deployment

```yaml
# k8s/mongodb-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: riesgo-ia
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: admin
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: riesgo-secrets
              key: mongo-password
        volumeMounts:
        - name: mongo-storage
          mountPath: /data/db
      volumes:
      - name: mongo-storage
        persistentVolumeClaim:
          claimName: mongo-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: riesgo-ia
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
```

---

### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: riesgo-ia
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry.com/riesgo-ia-backend:v1.0.0
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          value: "mongodb://admin:$(MONGO_PASSWORD)@mongodb:27017"
        - name: MONGO_PASSWORD
          valueFrom:
            secretKeyRef:
              name: riesgo-secrets
              key: mongo-password
        - name: EMERGENT_LLM_KEY
          valueFrom:
            secretKeyRef:
              name: riesgo-secrets
              key: emergent-llm-key
        envFrom:
        - configMapRef:
            name: riesgo-config
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: riesgo-ia
spec:
  selector:
    app: backend
  ports:
  - port: 8001
    targetPort: 8001
```

---

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: riesgo-ingress
  namespace: riesgo-ia
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "10"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - tu-dominio.com
    - api.tu-dominio.com
    secretName: riesgo-tls
  rules:
  - host: tu-dominio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: api.tu-dominio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8001
```

---

### Deploy to K8s

```bash
# Apply all
kubectl apply -f k8s/

# Watch pods
kubectl get pods -n riesgo-ia -w

# Check logs
kubectl logs -f deployment/backend -n riesgo-ia

# Scale
kubectl scale deployment backend --replicas=5 -n riesgo-ia

# Rollout update
kubectl set image deployment/backend backend=riesgo-ia-backend:v1.1.0 -n riesgo-ia
kubectl rollout status deployment/backend -n riesgo-ia

# Rollback
kubectl rollout undo deployment/backend -n riesgo-ia
```

---

## 🚀 CI/CD AUTOMATION

### GitHub Actions (Ya configurado)

**En cada push a `main`:**
1. Security scan
2. Lint & format check
3. Tests (unit + integration)
4. Build Docker images
5. Push to registry
6. Deploy to staging (automático)
7. Deploy to production (manual approval)

**Manual Approval:**
```yaml
deploy-production:
  needs: [build]
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://tu-dominio.com
  steps:
    # Deploy steps
```

---

## 📊 MONITORING

### Health Checks

```bash
# Backend health
curl https://api.tu-dominio.com/api/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "llm": {
    "provider": "gemini",
    "model": "gemini-2.5-flash",
    "configured": true
  }
}
```

---

### Logs

```bash
# Docker
docker logs -f riesgo-backend --tail 100

# Kubernetes
kubectl logs -f deployment/backend -n riesgo-ia --tail=100

# Grep errors
kubectl logs deployment/backend -n riesgo-ia | grep ERROR
```

---

## 🔄 ROLLBACK PROCEDURE

### Docker

```bash
# Ver imágenes anteriores
docker images riesgo-ia-backend

# Rollback
docker-compose down
docker-compose -f docker-compose.prod.yml up -d \
  --force-recreate \
  --no-deps \
  backend
```

### Kubernetes

```bash
# Ver history
kubectl rollout history deployment/backend -n riesgo-ia

# Rollback a versión anterior
kubectl rollout undo deployment/backend -n riesgo-ia

# Rollback a versión específica
kubectl rollout undo deployment/backend --to-revision=2 -n riesgo-ia
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

- [ ] Tests passing (CI green)
- [ ] Security scan passed
- [ ] Environment variables configuradas
- [ ] Secrets rotados (si aplica)
- [ ] Database backup reciente
- [ ] Rollback plan documentado
- [ ] Monitoring alertas configuradas
- [ ] Load testing realizado
- [ ] Stakeholders notificados

---

## 🆘 TROUBLESHOOTING

### Backend no inicia

```bash
# Check logs
docker logs riesgo-backend

# Errores comunes:
# 1. MongoDB no conectado → verificar MONGO_URL
# 2. API key inválida → verificar EMERGENT_LLM_KEY
# 3. Puerto ocupado → cambiar puerto o liberar

# Test conexión MongoDB
docker exec -it riesgo-backend python -c "from pymongo import MongoClient; print(MongoClient('mongodb://...').server_info())"
```

### Rate limiting muy agresivo

```bash
# Ajustar en .env
RATE_LIMIT_PER_MINUTE=20  # Aumentar

# Reiniciar
docker-compose restart backend
```

### Out of memory

```bash
# Aumentar límites en docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

---

## 📚 REFERENCIAS

- [Docker Docs](https://docs.docker.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Nginx Config](https://nginx.org/en/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Owner:** DevOps Team  
**Última actualización:** Enero 2025
