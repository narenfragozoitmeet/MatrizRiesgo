"""Esquema BRONZE - Datos crudos de ingesta

Tablas:
- documentos_raw: Documentos subidos sin procesar
- textos_extraidos: Texto extraído de documentos
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.sql import func
from db.session import Base

class DocumentoRaw(Base):
    """Documento crudo subido por el usuario"""
    __tablename__ = "documentos_raw"
    __table_args__ = {"schema": "bronze"}
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    empresa = Column(String, nullable=False)
    size_bytes = Column(Integer)
    
    # Metadata
    fecha_carga = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(JSON, default={})

class TextoExtraidoRaw(Base):
    """Texto extraído del documento (Agent_Extractor)"""
    __tablename__ = "textos_extraidos"
    __table_args__ = {"schema": "bronze"}
    
    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False, index=True)
    
    texto_crudo = Column(Text, nullable=False)
    texto_limpio = Column(Text, nullable=False)
    
    num_paginas = Column(Integer)
    num_palabras = Column(Integer)
    
    # Metadata de extracción
    metadata_extraccion = Column(JSON, default={})
    
    fecha_extraccion = Column(DateTime(timezone=True), server_default=func.now())