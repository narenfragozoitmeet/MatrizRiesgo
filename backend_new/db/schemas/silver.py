"""Esquema SILVER - Datos limpios y normalizados

Tablas:
- normativas_gtc45: Normativas y guías oficiales
- catalogo_peligros: Catálogo de peligros por clasificación
- catalogo_controles: Catálogo de controles SST
- peligros_identificados: Peligros detectados por Agent_Hazard_ID
- riesgos_mapeados: Riesgos asociados a peligros (Agent_Risk_Mapper)
- controles_planificados: Controles propuestos (Agent_Control_Planner)
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from db.session import Base
import enum

class TipoTareaEnum(str, enum.Enum):
    RUTINARIA = "Rutinaria"
    NO_RUTINARIA = "No Rutinaria"

class ClasificacionPeligroEnum(str, enum.Enum):
    FISICO = "Físico"
    QUIMICO = "Químico"
    BIOLOGICO = "Biológico"
    BIOMECANICO = "Biomecánico"
    PSICOSOCIAL = "Psicosocial"
    CONDICIONES_SEGURIDAD = "Condiciones de Seguridad"
    FENOMENOS_NATURALES = "Fenómenos Naturales"

# ==================== Catálogos ====================

class NormativaGTC45(Base):
    """Normativas y guías oficiales actualizadas"""
    __tablename__ = "normativas_gtc45"
    __table_args__ = {"schema": "silver"}
    
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String)  # "pdf", "web", "api"
    contenido = Column(Text)
    url_origen = Column(String)
    version = Column(String)
    
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(JSON, default={})

class CatalogoPeligro(Base):
    """Catálogo de peligros por clasificación"""
    __tablename__ = "catalogo_peligros"
    __table_args__ = {"schema": "silver"}
    
    id = Column(String, primary_key=True)
    clasificacion = Column(SQLEnum(ClasificacionPeligroEnum), nullable=False, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    fuentes_comunes = Column(JSON, default=[])
    efectos_tipicos = Column(JSON, default=[])
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

class CatalogoControl(Base):
    """Catálogo de controles SST por jerarquía"""
    __tablename__ = "catalogo_controles"
    __table_args__ = {"schema": "silver"}
    
    id = Column(String, primary_key=True)
    jerarquia = Column(String, nullable=False, index=True)  # Eliminación, Sustitución, etc.
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    aplicable_a = Column(JSON, default=[])  # Lista de clasificaciones de peligros
    sector_industria = Column(String)
    
    efectividad_estimada = Column(String)  # "Alta", "Media", "Baja"
    costo_estimado = Column(String)  # "Alto", "Medio", "Bajo"
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

# ==================== Resultados intermedios de Agentes ====================

class PeligroIdentificado(Base):
    """Peligros detectados por Agent_Hazard_ID"""
    __tablename__ = "peligros_identificados"
    __table_args__ = {"schema": "silver"}
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False, index=True)
    document_id = Column(String, nullable=False, index=True)
    
    # Estructura GTC 45
    proceso = Column(String, nullable=False)
    zona_lugar = Column(String)
    actividad = Column(String, nullable=False)
    tarea = Column(String, nullable=False)
    tipo_tarea = Column(SQLEnum(TipoTareaEnum), nullable=False)
    
    # Peligro
    clasificacion = Column(SQLEnum(ClasificacionPeligroEnum), nullable=False)
    descripcion_peligro = Column(Text, nullable=False)
    fuente = Column(String)
    medio = Column(String)
    individuo = Column(String)
    
    # Metadata del agente
    confianza = Column(Float, default=0.8)
    fuente_normativa = Column(String)
    
    fecha_identificacion = Column(DateTime(timezone=True), server_default=func.now())

class RiesgoMapeado(Base):
    """Riesgos asociados a peligros (Agent_Risk_Mapper)"""
    __tablename__ = "riesgos_mapeados"
    __table_args__ = {"schema": "silver"}
    
    id = Column(String, primary_key=True)
    peligro_id = Column(String, ForeignKey("silver.peligros_identificados.id"), nullable=False)
    task_id = Column(String, nullable=False, index=True)
    
    descripcion_riesgo = Column(Text, nullable=False)
    efectos_posibles = Column(JSON, default=[])
    peor_consecuencia = Column(String)
    personas_expuestas = Column(Integer, default=1)
    
    fecha_mapeo = Column(DateTime(timezone=True), server_default=func.now())

class ControlPlanificado(Base):
    """Controles propuestos por Agent_Control_Planner"""
    __tablename__ = "controles_planificados"
    __table_args__ = {"schema": "silver"}
    
    id = Column(String, primary_key=True)
    riesgo_id = Column(String, nullable=False)
    task_id = Column(String, nullable=False, index=True)
    
    jerarquia = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    justificacion = Column(Text)
    prioridad = Column(Integer, default=3)
    
    costo_estimado = Column(String)
    plazo_implementacion = Column(String)
    
    fecha_planificacion = Column(DateTime(timezone=True), server_default=func.now())