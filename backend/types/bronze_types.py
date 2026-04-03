"""Tipos para el esquema Bronze (datos crudos)"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class TextoExtraido(BaseModel):
    """Texto extraído por Agent_01_Extractor"""
    texto_crudo: str
    texto_limpio: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    num_paginas: Optional[int] = None
    num_palabras: Optional[int] = None
    idioma_detectado: str = "es"