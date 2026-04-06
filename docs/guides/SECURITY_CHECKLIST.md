# 🔒 SECURITY CHECKLIST

**Sistema:** Matriz de Riesgos SST  
**Última actualización:** Enero 2025

---

## 🚨 CRÍTICO - HACER INMEDIATAMENTE

### [ ] 1. Rotar API Key Expuesta

**Problema:** La key `sk-emergent-c6dBf0c1231Fd2aE78` está expuesta en `.env`

**Pasos:**

```bash
# 1. Generar nueva key
# Ir a: https://app.emergentagent.com/profile
# Sección: "Universal Key" → Generate New Key

# 2. Actualizar .env (NO commitear)
cd /app/backend
nano .env
# Reemplazar: EMERGENT_LLM_KEY=sk-emergent-NEW-KEY-HERE

# 3. Reiniciar servicios
sudo supervisorctl restart backend

# 4. Revocar key antigua en el dashboard

# 5. Verificar que .env NO esté en git
git status backend/.env  # No debe aparecer

# Si aparece, remover del tracking:
git rm --cached backend/.env
git commit -m "chore: Remove .env from tracking"
```

**Impacto si no se hace:** Uso no autorizado de tu cuenta, costos elevados, data breach.

---

### [ ] 2. Verificar .gitignore

```bash
# Verificar que .gitignore existe y tiene .env
cat /app/.gitignore | grep ".env"

# Debe contener:
# .env
# .env.*
# !.env.example

# Verificar archivos trackeados
git ls-files | grep ".env"
# Solo debe aparecer: backend/.env.example
```

---

### [ ] 3. MongoDB Authentication (Producción)

**Actual:** Sin autenticación (solo para desarrollo)

**Configuración Segura:**

```bash
# 1. Crear usuario admin en MongoDB
mongosh

use admin
db.createUser({
  user: "admin",
  pwd: "STRONG_PASSWORD_HERE",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase"]
})

use riesgo_ia
db.createUser({
  user: "riesgo_app",
  pwd: "ANOTHER_STRONG_PASSWORD",
  roles: [{ role: "readWrite", db: "riesgo_ia" }]
})

# 2. Habilitar auth en mongod.conf
sudo nano /etc/mongod.conf

# Añadir:
security:
  authorization: enabled

# 3. Reiniciar MongoDB
sudo systemctl restart mongod

# 4. Actualizar .env
MONGO_URL="mongodb://riesgo_app:ANOTHER_STRONG_PASSWORD@localhost:27017/riesgo_ia?authSource=riesgo_ia"

# 5. En producción, añadir SSL:
MONGO_URL="mongodb://user:pass@host:27017/?ssl=true&authSource=admin"
```

---

## 🟠 ALTO - HACER ESTA SEMANA

### [ ] 4. HTTPS/SSL Enforcement

```bash
# En producción, forzar HTTPS
# Nginx config:
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

---

### [ ] 5. Secrets Management

**Opciones:**

#### Opción A: AWS Secrets Manager (Recomendado para AWS)
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# En config.py:
EMERGENT_LLM_KEY = get_secret('prod/riesgo-ia/llm-key')
```

#### Opción B: HashiCorp Vault
```bash
# Instalar Vault
vault kv put secret/riesgo-ia/llm-key value="sk-emergent-..."

# En app:
import hvac
client = hvac.Client(url='http://vault:8200', token=os.environ['VAULT_TOKEN'])
secret = client.secrets.kv.v2.read_secret_version(path='riesgo-ia/llm-key')
```

#### Opción C: Docker Secrets (Para Docker Swarm)
```yaml
# docker-compose.yml
services:
  backend:
    secrets:
      - llm_key
      
secrets:
  llm_key:
    external: true
```

---

### [ ] 6. Configurar WAF (Web Application Firewall)

**Opciones:**

- **Cloudflare WAF** (Recomendado, fácil setup)
- **AWS WAF**
- **ModSecurity** (open source)

**Reglas Básicas:**
- Bloquear SQL injection patterns
- Bloquear XSS patterns
- Rate limiting por IP
- Geoblocking (opcional)

---

### [ ] 7. Dependency Scanning

```bash
# Python - Safety
cd backend
pip install safety
safety check --full-report

# Python - Bandit (security linter)
pip install bandit
bandit -r . -f json -o security-report.json

# Frontend - NPM Audit
cd frontend
npm audit
npm audit fix  # Solo si no rompe nada

# Configurar en CI/CD (ya incluido en .github/workflows/ci-cd.yml)
```

---

## 🟡 MEDIO - HACER ESTE MES

### [ ] 8. Implementar API Key Rotation

```python
# backend/core/api_key_manager.py
from datetime import datetime, timedelta

class APIKeyManager:
    def should_rotate(self, created_at: datetime) -> bool:
        """Rotar cada 90 días"""
        return datetime.now() - created_at > timedelta(days=90)
    
    def notify_rotation_needed(self):
        # Enviar email/slack
        pass
```

---

### [ ] 9. Audit Logging

```python
# backend/shared/audit_logger.py
import structlog

audit_logger = structlog.get_logger("audit")

def log_security_event(event_type: str, user_id: str, details: dict):
    audit_logger.info(
        "security_event",
        type=event_type,
        user_id=user_id,
        timestamp=datetime.now().isoformat(),
        **details
    )

# Usar en:
# - Login attempts
# - Failed authentication
# - API key usage
# - Admin actions
# - Data exports
```

---

### [ ] 10. Implementar CSP (Content Security Policy)

```python
# En server.py middleware:
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https://api.emergentagent.com;"
)
```

---

### [ ] 11. Backup & Disaster Recovery

```bash
# MongoDB Backup (cron diario)
#!/bin/bash
# /scripts/backup_mongodb.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/mongodb"

mongodump --uri="mongodb://user:pass@localhost:27017/riesgo_ia" \
  --out="$BACKUP_DIR/$DATE"

# Comprimir
tar -czf "$BACKUP_DIR/riesgo_ia_$DATE.tar.gz" "$BACKUP_DIR/$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Upload a S3
aws s3 cp "$BACKUP_DIR/riesgo_ia_$DATE.tar.gz" s3://backups/mongodb/

# Retener últimos 30 días
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Crontab:
# 0 3 * * * /scripts/backup_mongodb.sh
```

---

## 📋 CHECKLIST SEMANAL

### Cada Lunes:
- [ ] Revisar logs de errores (Sentry)
- [ ] Revisar intentos de login fallidos
- [ ] Verificar rate limiting funcionando
- [ ] Check disk space / memoria
- [ ] Revisar alertas de monitoreo

### Cada Mes:
- [ ] Actualizar dependencias (npm audit, pip list --outdated)
- [ ] Revisar access logs sospechosos
- [ ] Rotar logs viejos
- [ ] Backup verification (restaurar backup de prueba)
- [ ] Revisar usuarios con acceso a producción

### Cada Cuatrimestre:
- [ ] Penetration testing
- [ ] Security audit externo
- [ ] Revisar políticas de acceso
- [ ] Actualizar documentación de seguridad
- [ ] Rotar API keys

---

## 🛡️ SECURITY BEST PRACTICES

### Desarrollo

```python
# ✅ HACER
from shared.exceptions import ValidationError

def process_input(data: str):
    if not data or len(data) > 10000:
        raise ValidationError("Input inválido")
    # Sanitizar antes de usar
    return sanitize(data)

# ❌ NO HACER
def process_input(data):
    # Sin validación, vulnerable
    return data
```

### Base de Datos

```python
# ✅ HACER - Usar ORM/parametrizado
result = db.matrices_sst.find_one({"_id": matriz_id})

# ❌ NO HACER - SQL Injection vulnerable
query = f"SELECT * FROM matrices WHERE id = '{matriz_id}'"
```

### Secrets

```python
# ✅ HACER
API_KEY = os.environ.get('EMERGENT_LLM_KEY')
if not API_KEY:
    raise ValueError("API key no configurada")

# ❌ NO HACER
API_KEY = "sk-emergent-hardcoded-key-here"  # NUNCA
```

---

## 🚨 INCIDENTE - QUÉ HACER

### Si detectas una brecha de seguridad:

1. **Contener:**
   - Desconectar servidor afectado
   - Revocar API keys comprometidas
   - Cambiar contraseñas

2. **Evaluar:**
   - ¿Qué datos fueron expuestos?
   - ¿Cuántos usuarios afectados?
   - ¿Cuándo ocurrió?

3. **Remediar:**
   - Parchear vulnerabilidad
   - Restaurar desde backup limpio
   - Actualizar dependencias

4. **Notificar:**
   - Informar a usuarios afectados
   - Reportar a autoridades (GDPR si aplica)
   - Documentar el incidente

5. **Prevenir:**
   - Post-mortem
   - Actualizar prácticas
   - Mejorar monitoreo

---

## 📞 CONTACTOS DE EMERGENCIA

- **Security Lead:** [email]
- **DevOps On-call:** [phone]
- **Legal:** [email]
- **Sentry Alerts:** [slack-channel]

---

## 📚 REFERENCIAS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Última revisión:** Enero 2025  
**Próxima revisión:** Febrero 2025  
**Owner:** Security Team
