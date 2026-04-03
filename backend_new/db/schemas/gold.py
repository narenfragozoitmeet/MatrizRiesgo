"""Esquema GOLD - Datos finales del negocio

Tablas:
- matrices_gtc45: Matrices finales GTC 45 listas para exportar
- matrices_ram: Matrices RAM (si aplica)
- exportaciones: Registro de archivos Excel generados
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from db.session import Base

class MatrizGTC45(Base):
    """Matriz GTC 45 final lista para negocio"""
    __tablename__ = "matrices_gtc45"
    __table_args__ = {"schema": "gold"}
    
    id = Column(String, primary_key=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    document_id = Column(String, nullable=False, index=True)
    
    # Info de la empresa
    nombre_empresa = Column(String, nullable=False)
    documento_origen = Column(String, nullable=False)
    
    # Responsables
    responsable_elaboracion = Column(String, default="Sistema Riesgo IA")
    responsable_revision = Column(String)
    responsable_aprobacion = Column(String)
    
    # Estructura completa de la matriz (JSON)
    riesgos = Column(JSON, nullable=False)  # Lista de RiesgoCompleto
    
    # Resumen ejecutivo
    resumen_ejecutivo = Column(Text)
    
    # Estadísticas
    total_riesgos = Column(Integer, default=0)
    riesgos_criticos = Column(Integer, default=0)  # Nivel I
    riesgos_altos = Column(Integer, default=0)     # Nivel II
    riesgos_medios = Column(Integer, default=0)    # Nivel III
    riesgos_bajos = Column(Integer, default=0)     # Nivel IV
    
    por_clasificacion = Column(JSON, default={})
    por_proceso = Column(JSON, default={})
    
    # Metadatos
    version = Column(String, default="1.0")
    estado = Column(String, default="draft")  # draft, reviewed, approved
    
    # Fechas
    fecha_elaboracion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_revision = Column(DateTime(timezone=True))
    fecha_aprobacion = Column(DateTime(timezone=True))
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Control de cambios
    historial_cambios = Column(JSON, default=[])

class MatrizRAM(Base):
    """Matriz RAM (Risk Assessment Matrix) - Opcional"""
    __tablename__ = "matrices_ram"
    __table_args__ = {"schema": "gold"}
    
    id = Column(String, primary_key=True)
    matriz_gtc45_id = Column(String, nullable=False, index=True)
    
    # Evaluación RAM
    riesgos_ram = Column(JSON, nullable=False)
    
    # Resumen por dimensión
    resumen_personas = Column(JSON, default={})
    resumen_economico = Column(JSON, default={})
    resumen_ambiental = Column(JSON, default={})
    resumen_clientes = Column(JSON, default={})
    resumen_reputacion = Column(JSON, default={})
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

class Exportacion(Base):
    """Registro de exportaciones a Excel"""
    __tablename__ = "exportaciones"
    __table_args__ = {"schema": "gold"}
    
    id = Column(String, primary_key=True)
    matriz_gtc45_id = Column(String, nullable=False, index=True)
    
    formato = Column(String, default="xlsx")  # xlsx, pdf, docx
    plantilla_usada = Column(String)
    
    storage_path = Column(String)
    filename = Column(String)
    size_bytes = Column(Integer)
    
    # Metadata
    incluye_ram = Column(Boolean, default=False)
    incluye_graficos = Column(Boolean, default=False)
    
    fecha_exportacion = Column(DateTime(timezone=True), server_default=func.now())
    exportado_por = Column(String)