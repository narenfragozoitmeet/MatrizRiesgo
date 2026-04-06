"""Tests unitarios para validadores"""

import pytest
from shared.validators import DocumentValidator, TextValidator
from shared.exceptions import FileTooLargeError, UnsupportedFileTypeError, ValidationError


class TestDocumentValidator:
    """Tests para DocumentValidator"""
    
    def test_validate_file_success_pdf(self):
        """Test validación exitosa de PDF"""
        DocumentValidator.validate_file(
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024 * 1024  # 1MB
        )
        # No debería lanzar excepción
    
    def test_validate_file_success_docx(self):
        """Test validación exitosa de DOCX"""
        DocumentValidator.validate_file(
            filename="test.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=2 * 1024 * 1024  # 2MB
        )
    
    def test_validate_file_too_large(self):
        """Test archivo muy grande"""
        with pytest.raises(FileTooLargeError):
            DocumentValidator.validate_file(
                filename="huge.pdf",
                content_type="application/pdf",
                file_size=50 * 1024 * 1024  # 50MB > 10MB límite
            )
    
    def test_validate_file_unsupported_type(self):
        """Test tipo de archivo no soportado"""
        with pytest.raises(UnsupportedFileTypeError):
            DocumentValidator.validate_file(
                filename="virus.exe",
                content_type="application/x-msdownload",
                file_size=1024
            )
    
    def test_validate_file_wrong_extension(self):
        """Test extensión incorrecta"""
        with pytest.raises(UnsupportedFileTypeError):
            DocumentValidator.validate_file(
                filename="malicious.pdf.exe",
                content_type="application/pdf",
                file_size=1024
            )


class TestTextValidator:
    """Tests para TextValidator"""
    
    def test_validate_text_success(self):
        """Test validación exitosa de texto"""
        long_text = "A" * 200
        result = TextValidator.validate_text(long_text)
        assert result == long_text
    
    def test_validate_text_too_short(self):
        """Test texto muy corto"""
        with pytest.raises(ValidationError):
            TextValidator.validate_text("abc")
    
    def test_validate_text_truncates_if_too_long(self):
        """Test truncado de texto muy largo"""
        very_long_text = "A" * 600000  # 600KB
        result = TextValidator.validate_text(very_long_text)
        assert len(result) <= 500000
    
    def test_sanitize_for_llm(self):
        """Test sanitización para LLM"""
        text = "A" * 20000
        result = TextValidator.sanitize_for_llm(text)
        assert len(result) <= 15000
    
    def test_sanitize_removes_control_chars(self):
        """Test remoción de caracteres de control"""
        text = "Hello\x00World\x01Test"
        result = TextValidator.sanitize_for_llm(text)
        assert "\x00" not in result
        assert "\x01" not in result
