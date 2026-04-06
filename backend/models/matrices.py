"""Modelos Pydantic para Matrices de Riesgos"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

# ============================================
# MODELOS COMUNES
# ============================================

class TipoMatriz(str, Enum):
    """Tipo de matriz a generar"""
    SST = "sst"  # Seguridad y Salud en el Trabajo (GTC 45)
    LEGAL = "legal"  # Riesgos Legales

class NivelRiesgo(str, Enum):
    """Niveles de riesgo según metodología RAM"""
    CRITICO = "Crítico"
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"
    TRIVIAL = "Trivial"

# ============================================
# MATRIZ SST (GTC 45)
# ============================================

class PeligroSST(BaseModel):
    """Peligro identificado según GTC 45"""
    clasificacion: str  # Físico, Químico, Biológico, Ergonómico, etc.
    descripcion: str
    fuente: str  # De dónde se extrajo
    efectos_posibles: List[str]

class RiesgoSST(BaseModel):
    """Riesgo evaluado según GTC 45"""
    id_riesgo: str
    proceso: str
    zona_lugar: str
    actividad: str
    peligro: PeligroSST
    
    # Evaluación del riesgo
    nivel_deficiencia: int  # 0-10
    nivel_exposicion: int  # 1-4
    nivel_probabilidad: int  # ND x NE
    interpretacion_probabilidad: str  # Muy Alta, Alta, Media, Baja
    
    nivel_consecuencia: int  # 10, 25, 60, 100
    nivel_riesgo: int  # NP x NC
    interpretacion_riesgo: NivelRiesgo
    
    # Controles
    controles_existentes: List[str]
    controles_propuestos: List[str]
    
    # Metodología
    metodologia: str = "GTC 45 + RAM"
    aceptabilidad: str  # Aceptable, No Aceptable

class MatrizSST(BaseModel):
    """Matriz completa SST (GTC 45)"""
    id: Optional[str] = None
    tipo_matriz: TipoMatriz = TipoMatriz.SST
    
    # Información empresa
    empresa: str
    documento_origen: str
    document_id: str
    
    # Riesgos
    riesgos: List[RiesgoSST]
    
    # Estadísticas
    total_riesgos: int
    riesgos_criticos: int
    riesgos_altos: int
    riesgos_medios: int
    riesgos_bajos: int
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    metodologia: str = "GTC 45 (Guía Técnica Colombiana) + RAM (Risk Assessment Matrix)"
    estado: str = "generada"

# ============================================
# MATRIZ RIESGOS LEGALES
# ============================================

class CategoriaRiesgoLegal(str, Enum):
    """Categorías de riesgos legales"""
    CONTRACTUAL = "Contractual"
    CUMPLIMIENTO = "Cumplimiento Normativo"
    LABORAL = "Laboral"
    FISCAL = "Fiscal"
    REGULATORIO = "Regulatorio"
    PROPIEDAD_INTELECTUAL = "Propiedad Intelectual"
    AMBIENTAL = "Ambiental"
    PROTECCION_DATOS = "Protección de Datos"
    CORPORATIVO = "Corporativo"
    LITIGIOS = "Litigios"

class RiesgoLegal(BaseModel):
    """Riesgo legal identificado"""
    id_riesgo: str
    categoria: CategoriaRiesgoLegal
    descripcion: str
    fuente_documento: str  # De dónde se identificó
    
    # Evaluación
    probabilidad_ocurrencia: int  # 1-5
    impacto_financiero: int  # 1-5
    impacto_reputacional: int  # 1-5
    impacto_operacional: int  # 1-5
    
    # Cálculo RAM
    nivel_riesgo_calculado: int  # Prob x (ImpFin + ImpRep + ImpOp)/3
    nivel_riesgo: NivelRiesgo
    
    # Contexto legal
    normativa_aplicable: List[str]
    clausulas_relevantes: List[str]
    
    # Mitigación
    controles_actuales: List[str]
    acciones_mitigacion: List[str]
    responsable_sugerido: str
    
    # Metodología
    metodologia: str = "RAM + Análisis Normativo"
    prioridad: str  # Inmediata, Alta, Media, Baja

class MatrizLegal(BaseModel):
    """Matriz completa de Riesgos Legales"""
    id: Optional[str] = None
    tipo_matriz: TipoMatriz = TipoMatriz.LEGAL
    
    # Información empresa
    empresa: str
    documento_origen: str
    document_id: str
    
    # Riesgos
    riesgos: List[RiesgoLegal]
    
    # Estadísticas
    total_riesgos: int
    riesgos_criticos: int
    riesgos_altos: int
    riesgos_medios: int
    riesgos_bajos: int
    
    # Distribución por categoría
    distribucion_categorias: dict  # {categoria: count}
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    metodologia: str = "RAM (Risk Assessment Matrix) + Análisis Legal Normativo"
    estado: str = "generada"

# ============================================
# MODELOS PARA APIs
# ============================================

class IngestRequest(BaseModel):
    """Request para ingesta de documento"""
    empresa: str
    tipo_matriz: TipoMatriz
    descripcion_contexto: Optional[str] = None

class TaskStatus(BaseModel):
    """Estado de procesamiento"""
    task_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: Optional[str] = None
    matriz_id: Optional[str] = None
    error: Optional[str] = None

class MatrizResumen(BaseModel):
    """Resumen de matriz para listados"""
    id: str
    tipo_matriz: TipoMatriz
    empresa: str
    documento_origen: str
    total_riesgos: int
    riesgos_criticos: int
    created_at: datetime
    estado: str
