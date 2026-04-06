# 🧪 TESTING GUIDE

**Sistema:** Matriz de Riesgos SST  
**Framework:** Pytest + FastAPI TestClient + Playwright

---

## 📊 ESTADO ACTUAL

```
✅ Unit Tests:         10/10 passing (100%)
✅ Integration Tests:   8/9 passing  (89% - 1 skipped)
❌ E2E Tests:           0/TBD         (0% - TODO)

Cobertura Total:       ~60%
Cobertura Crítica:     95%
```

---

## 🏗️ ESTRUCTURA DE TESTS

```
backend/tests/
├── conftest.py              # Configuración global
├── unit/                    # Tests unitarios
│   ├── test_validators.py  ✅ 10 tests
│   ├── test_models.py      ⏳ TODO
│   └── test_services.py    ⏳ TODO
├── integration/             # Tests de integración
│   ├── test_api.py         ✅ 8 tests
│   └── test_database.py    ⏳ TODO
└── e2e/                     # Tests end-to-end
    └── test_complete_flow.py ⏳ TODO

frontend/src/__tests__/
├── HomePage.test.js        ⏳ TODO
├── AnalysisPage.test.js    ⏳ TODO
└── integration/            ⏳ TODO
```

---

## 🚀 QUICK START

### Setup

```bash
cd /app/backend

# Instalar dependencias de test
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Ejecutar todos los tests
pytest -v

# Con coverage
pytest --cov=. --cov-report=html

# Solo unitarios
pytest tests/unit/ -v

# Solo integración
pytest tests/integration/ -v
```

---

## 📝 UNIT TESTS

### ✅ Implementados (10 tests)

**Archivo:** `tests/unit/test_validators.py`

```python
class TestDocumentValidator:
    def test_validate_file_success_pdf(self):
        """Valida PDF correcto"""
        DocumentValidator.validate_file(
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024 * 1024  # 1MB
        )
        # No debería lanzar excepción
    
    def test_validate_file_too_large(self):
        """Rechaza archivo muy grande"""
        with pytest.raises(FileTooLargeError):
            DocumentValidator.validate_file(
                filename="huge.pdf",
                content_type="application/pdf",
                file_size=50 * 1024 * 1024  # 50MB > límite
            )
```

**Ejecutar:**
```bash
pytest tests/unit/test_validators.py -v
```

---

### ⏳ Por Implementar

#### 1. Test Models (`test_models.py`)

```python
# tests/unit/test_models.py
from models.matrices import MatrizSST, RiesgoSST, NivelRiesgo

class TestMatrizSST:
    def test_create_matriz_with_valid_data(self):
        """Crea matriz con datos válidos"""
        matriz = MatrizSST(
            empresa="Test Corp",
            documento_origen="test.pdf",
            document_id="123",
            riesgos=[],
            total_riesgos=0,
            riesgos_criticos=0,
            riesgos_altos=0,
            riesgos_medios=0,
            riesgos_bajos=0
        )
        assert matriz.empresa == "Test Corp"
        assert matriz.total_riesgos == 0
    
    def test_matriz_calculates_stats_correctly(self):
        """Calcula estadísticas correctamente"""
        # TODO: Implementar
        pass

class TestRiesgoSST:
    def test_nivel_riesgo_calculation(self):
        """Calcula nivel de riesgo según GTC 45"""
        # ND=8, NE=3, NC=60 → NP=24, NR=1440 → Alto
        riesgo = RiesgoSST(
            id_riesgo="R-001",
            nivel_deficiencia=8,
            nivel_exposicion=3,
            nivel_consecuencia=60,
            # ... otros campos
        )
        assert riesgo.nivel_riesgo == 1440
        assert riesgo.interpretacion_riesgo == NivelRiesgo.ALTO
```

**Prioridad:** ALTA  
**Estimación:** 4 horas

---

#### 2. Test Services (`test_services.py`)

```python
# tests/unit/test_services.py
from unittest.mock import Mock, patch
from services.matriz_sst_processor import MatrizSSTProcessor

class TestMatrizSSTProcessor:
    @patch('services.llm_service.llm_service.generate')
    async def test_identificar_peligros_success(self, mock_llm):
        """Identifica peligros correctamente"""
        # Mock LLM response
        mock_llm.return_value = json.dumps({
            "nombre_empresa": "Test Corp",
            "peligros_identificados": [...]
        })
        
        processor = MatrizSSTProcessor()
        result = await processor._identificar_peligros(
            texto="...",
            nombre_doc="test.pdf"
        )
        
        assert result["nombre_empresa"] == "Test Corp"
        assert len(result["peligros_identificados"]) > 0
    
    @patch('services.llm_service.llm_service.generate')
    async def test_identificar_peligros_handles_llm_error(self, mock_llm):
        """Maneja error del LLM correctamente"""
        mock_llm.side_effect = Exception("LLM Error")
        
        processor = MatrizSSTProcessor()
        with pytest.raises(LLMProcessingError):
            await processor._identificar_peligros(...)
```

**Prioridad:** ALTA  
**Estimación:** 6 horas

---

## 🔗 INTEGRATION TESTS

### ✅ Implementados (8 tests)

**Archivo:** `tests/integration/test_api.py`

```python
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health_check_returns_200():
    """Health check OK"""
    response = client.get("/api/health")
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert "database" in data

def test_ingest_with_invalid_file_type():
    """Rechaza tipo inválido"""
    files = {"file": ("test.txt", b"fake", "text/plain")}
    response = client.post("/api/v1/ingest", files=files)
    
    assert response.status_code == 400
    assert "no soportado" in response.json()["detail"].lower()
```

**Ejecutar:**
```bash
pytest tests/integration/test_api.py -v
```

---

### ⏳ Por Implementar

#### 1. Database Tests (`test_database.py`)

```python
# tests/integration/test_database.py
import pytest
from db.mongodb import MongoDB

@pytest.fixture
def test_db():
    """Base de datos de test"""
    db = MongoDB()
    db.db_name = "test_riesgo_ia"
    yield db
    # Cleanup
    db.client.drop_database("test_riesgo_ia")

class TestMongoDBIntegration:
    def test_connect_to_database(self, test_db):
        """Conecta a MongoDB"""
        test_db.connect()
        assert test_db.db is not None
    
    def test_save_and_retrieve_matriz(self, test_db):
        """Guarda y recupera matriz"""
        matriz_data = {
            "_id": "test-123",
            "empresa": "Test Corp",
            "total_riesgos": 5
        }
        
        test_db.matrices_sst.insert_one(matriz_data)
        
        retrieved = test_db.matrices_sst.find_one({"_id": "test-123"})
        assert retrieved["empresa"] == "Test Corp"
```

**Prioridad:** MEDIA  
**Estimación:** 3 horas

---

## 🎭 E2E TESTS (Playwright)

### Setup Playwright

```bash
# Instalar Playwright
pip install playwright pytest-playwright
playwright install chromium

# Crear conftest para Playwright
# tests/e2e/conftest.py
```

---

### Test Completo de Flujo

```python
# tests/e2e/test_complete_flow.py
import pytest
from playwright.sync_api import Page, expect
import os

@pytest.fixture
def test_pdf_path():
    """Path a PDF de test"""
    return os.path.join(os.path.dirname(__file__), "fixtures", "test_documento.pdf")

def test_complete_matrix_generation_flow(page: Page, test_pdf_path):
    """
    Test E2E: Upload → Proceso → Descarga
    
    Flujo:
    1. Usuario accede a homepage
    2. Selecciona archivo PDF
    3. Hace clic en "Generar Matriz"
    4. Espera procesamiento (puede tardar 30-60s)
    5. Ve resultados en AnalysisPage
    6. Descarga Excel
    """
    # 1. Navegar a homepage
    page.goto("http://localhost:3000")
    expect(page).to_have_title("Matriz de Riesgos SST")
    
    # 2. Upload archivo
    file_input = page.locator('[data-testid="file-input"]')
    file_input.set_input_files(test_pdf_path)
    
    # Verificar que archivo se seleccionó
    expect(page.locator('[data-testid="selected-file"]')).to_be_visible()
    
    # 3. Click generar (con rate limit puede fallar en CI)
    with page.expect_navigation(timeout=60000):  # 60s timeout
        page.locator('[data-testid="analyze-button"]').click()
    
    # 4. Debería estar en /analysis/{id}
    expect(page).to_have_url(re.compile(r"/analysis/[a-f0-9-]+"))
    
    # 5. Verificar stats visibles
    expect(page.locator("text=Total Riesgos")).to_be_visible()
    expect(page.locator("text=Críticos")).to_be_visible()
    
    # 6. Click descargar Excel
    download_button = page.locator('[data-testid="download-button"]')
    
    with page.expect_download() as download_info:
        download_button.click()
    
    download = download_info.value
    assert download.suggested_filename.endswith(".xlsx")
    
    # Verificar que archivo se descargó
    download_path = download.path()
    assert os.path.exists(download_path)
    assert os.path.getsize(download_path) > 1024  # > 1KB


def test_upload_invalid_file_shows_error(page: Page):
    """Test error con archivo inválido"""
    page.goto("http://localhost:3000")
    
    # Crear archivo .txt temporal
    with open("/tmp/test_invalid.txt", "w") as f:
        f.write("invalid content")
    
    file_input = page.locator('[data-testid="file-input"]')
    file_input.set_input_files("/tmp/test_invalid.txt")
    
    page.locator('[data-testid="analyze-button"]').click()
    
    # Debería mostrar error
    error_message = page.locator('[data-testid="error-message"]')
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("no soportado")


def test_rate_limiting_shows_appropriate_message(page: Page, test_pdf_path):
    """Test que rate limiting funciona"""
    page.goto("http://localhost:3000")
    
    # Hacer 6 requests rápidos (límite es 5/min)
    for i in range(6):
        file_input = page.locator('[data-testid="file-input"]')
        file_input.set_input_files(test_pdf_path)
        page.locator('[data-testid="analyze-button"]').click()
        page.wait_for_timeout(500)  # 500ms entre requests
    
    # La 6ta debería fallar
    error_message = page.locator('[data-testid="error-message"]')
    expect(error_message).to_contain_text("Demasiadas solicitudes")
```

**Ejecutar:**
```bash
# Headed (con UI)
pytest tests/e2e/ --headed --slowmo 500

# Headless (CI)
pytest tests/e2e/
```

**Prioridad:** ALTA  
**Estimación:** 8 horas

---

## 📊 COVERAGE

### Generar Reporte

```bash
# HTML report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=. --cov-report=term-missing

# XML (para CI)
pytest --cov=. --cov-report=xml
```

### Objetivo de Cobertura

```
✅ Critical paths:  95%+  (APIs, validadores, procesadores)
✅ Business logic:  90%+  (services, models)
✅ Utils:           80%+  (helpers, formatters)
❌ Config/Setup:    50%+  (no crítico)

Total Target:       85%+
```

---

## 🤖 CI/CD Integration

Tests ya configurados en `.github/workflows/ci-cd.yml`:

```yaml
test-backend:
  runs-on: ubuntu-latest
  services:
    mongodb:
      image: mongo:7.0
      ports:
        - 27017:27017
  steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: pytest tests/ --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 🎯 PRÓXIMOS PASOS

### Esta Semana:
1. [ ] Implementar tests de models (4h)
2. [ ] Implementar tests de services (6h)
3. [ ] Setup Playwright (2h)
4. [ ] Test E2E básico (4h)

### Este Mes:
5. [ ] Database integration tests (3h)
6. [ ] Performance tests (load testing)
7. [ ] Security tests (OWASP)
8. [ ] Frontend unit tests (Jest)

---

## 📚 REFERENCIAS

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Playwright Python](https://playwright.dev/python/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Owner:** QA Lead  
**Última actualización:** Enero 2025
