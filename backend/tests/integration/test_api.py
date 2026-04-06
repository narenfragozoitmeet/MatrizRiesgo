"""Tests de integración para API"""

import pytest
from fastapi.testclient import TestClient
from server import app
from io import BytesIO

client = TestClient(app)


class TestHealthEndpoint:
    """Tests para endpoint de health check"""
    
    def test_health_check_returns_200(self):
        """Test health check retorna 200"""
        response = client.get("/api/health")
        assert response.status_code in [200, 503]  # 503 si MongoDB no conectado
        
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "llm" in data
    
    def test_root_endpoint(self):
        """Test endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["app"] == "Riesgo IA"
        assert "version" in data
        assert "metodologias" in data


class TestInfoRequisitos:
    """Tests para endpoint de info requisitos"""
    
    def test_info_requisitos_returns_data(self):
        """Test info-requisitos retorna estructura correcta"""
        response = client.get("/api/v1/info-requisitos")
        assert response.status_code == 200
        
        data = response.json()
        assert "title" in data
        assert "description" in data
        assert "document_types" in data
        assert len(data["document_types"]) == 3  # PDF, Word, Excel


class TestMatricesList:
    """Tests para endpoint de listado de matrices"""
    
    def test_list_matrices_returns_array(self):
        """Test listado retorna array"""
        response = client.get("/api/v1/matrices")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestIngestEndpoint:
    """Tests para endpoint de ingesta"""
    
    def test_ingest_without_file_returns_422(self):
        """Test ingesta sin archivo retorna error"""
        response = client.post("/api/v1/ingest")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_ingest_with_invalid_file_type(self):
        """Test ingesta con tipo inválido"""
        file_content = b"fake content"
        files = {"file": ("test.txt", file_content, "text/plain")}
        
        response = client.post("/api/v1/ingest", files=files)
        assert response.status_code == 400
        assert "no soportado" in response.json()["detail"].lower()
    
    @pytest.mark.skip(reason="Requiere archivo PDF real y LLM activo")
    def test_ingest_success_with_valid_pdf(self):
        """Test ingesta exitosa con PDF válido"""
        # Este test requeriría un PDF real y LLM configurado
        pass


class TestMatrixEndpoints:
    """Tests para endpoints de matriz"""
    
    def test_get_nonexistent_matrix_returns_404(self):
        """Test obtener matriz inexistente retorna 404"""
        response = client.get("/api/v1/matrix/nonexistent-id")
        assert response.status_code == 404
    
    def test_export_nonexistent_matrix_returns_404(self):
        """Test exportar matriz inexistente retorna 404"""
        response = client.get("/api/v1/matrix/nonexistent-id/export")
        assert response.status_code == 404
