# 🔐 Guía de Implementación de Seguridad

## ✅ Implementado

### 1. Autenticación JWT
- **Endpoints creados:**
  - `POST /api/v1/auth/register` - Registro de usuarios
  - `POST /api/v1/auth/login` - Login (retorna JWT)
  - `GET /api/v1/auth/me` - Info del usuario actual
  - `POST /api/v1/auth/logout` - Logout

- **Uso en código:**
```python
from core.security import get_current_user, get_current_user_optional

# Endpoint protegido (requiere auth)
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["sub"]}

# Endpoint opcional (funciona con o sin auth)
@router.get("/optional")
async def optional_route(current_user: dict = Depends(get_current_user_optional)):
    if current_user:
        return {"message": f"Hello {current_user['email']}"}
    return {"message": "Hello anonymous"}
```

### 2. Gestión de Credenciales
- ✅ `.env.example` creado con placeholders
- ✅ `.env` agregado a `.gitignore`
- ✅ Sin defaults sensibles en `config.py`
- ✅ JWT_SECRET_KEY generada con openssl

### 3. CORS Mejorado
- ✅ Validación que previene wildcard en producción
- ✅ Error si `allow_credentials=True` con `*`

### 4. Manejo de Errores
- ✅ Mensajes genéricos en producción
- ✅ Detalles completos en desarrollo
- ✅ Logging estructurado con structlog

### 5. Dockerfile Non-Root
- ✅ Usuario `appuser` creado
- ✅ Contenedor ejecuta como non-root

---

## 🔄 Pendiente - Aplicar a Endpoints

### Endpoints que DEBEN protegerse:

```python
# sst_api.py
@router.post("/ingest")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def ingest_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)  # ← AGREGAR
):
    # ... código existente
    # Asociar matriz al usuario:
    # matriz["user_id"] = current_user["sub"]
```

```python
@router.get("/matrices", response_model=List[MatrizResponse])
async def list_matrices(
    request: Request,
    current_user: dict = Depends(get_current_user)  # ← AGREGAR
):
    # Filtrar por usuario:
    # matrices = await db.matrices_sst.find(
    #     {"user_id": current_user["sub"]},
    #     {"_id": 0}
    # ).to_list(100)
```

```python
@router.get("/matrix/{matriz_id}")
async def get_matriz(
    request: Request,
    matriz_id: str,
    current_user: dict = Depends(get_current_user)  # ← AGREGAR
):
    # Verificar ownership:
    # if matriz["user_id"] != current_user["sub"] and not current_user.get("is_admin"):
    #     raise HTTPException(403, "No tienes permiso")
```

### Endpoints que pueden ser públicos:
- `GET /info-requisitos` - Información general
- `GET /api/health` - Health check
- `GET /` - Root endpoint

---

## 📋 Checklist de Seguridad

### Pre-Deploy
- [ ] Verificar que `.env` está en `.gitignore`
- [ ] Rotar `EMERGENT_LLM_KEY` si fue expuesta
- [ ] Generar nueva `JWT_SECRET_KEY` para producción
- [ ] Configurar `CORS_ORIGINS` con dominios reales
- [ ] Cambiar `ENVIRONMENT=production`
- [ ] Cambiar `DEBUG=false`

### Monitoreo
- [ ] Configurar alertas para rate limiting
- [ ] Monitorear logs de autenticación fallida
- [ ] Dashboard de métricas de seguridad

### Actualizaciones
- [ ] Actualizar dependencias regularmente: `pip list --outdated`
- [ ] Revisar CVEs de dependencias
- [ ] Backup regular de base de datos

---

## 🛡️ Mejores Prácticas

### Passwords
- Mínimo 8 caracteres (configurado en `UserCreate`)
- Bcrypt para hashing (configurado en `AuthService`)
- No guardar passwords en logs

### Tokens JWT
- Expiración: 24 horas (configurable en `JWT_EXPIRATION_MINUTES`)
- Almacenar en localStorage o httpOnly cookie en frontend
- Enviar en header: `Authorization: Bearer {token}`

### Rate Limiting
- Actual: 5 requests/minuto (configurable)
- Aplicado a endpoints sensibles con `@limiter.limit()`

### HTTPS
- Obligatorio en producción
- Configurar en reverse proxy (Nginx/Caddy)
- HSTS header ya configurado en `SecurityHeadersMiddleware`

---

## 🔧 Testing de Seguridad

```bash
# 1. Intentar acceder sin token
curl -X GET "$API_URL/api/v1/matrices"
# Debe retornar 401 Unauthorized

# 2. Intentar con token inválido
curl -X GET "$API_URL/api/v1/matrices" \
  -H "Authorization: Bearer invalid_token"
# Debe retornar 401 Unauthorized

# 3. Intentar con token válido
TOKEN=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test12345"}' \
  | jq -r '.access_token')

curl -X GET "$API_URL/api/v1/matrices" \
  -H "Authorization: Bearer $TOKEN"
# Debe retornar 200 OK con datos del usuario
```

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
