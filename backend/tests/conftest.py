"""Configuración de pytest"""

import pytest
import sys
from pathlib import Path

# Añadir backend al path para imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session")
def test_config():
    """Configuración de test"""
    return {
        "test_mode": True,
        "db_name": "test_riesgo_ia"
    }
