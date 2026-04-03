"""Tipos para el esquema Silver (datos procesados)"""

from pydantic import BaseModel, Field
from typing import List, Optional
from types.base_types import ClasificacionPeligro, TipoTarea, JerarquiaControl

class PeligroIdentificado(BaseModel):
    """Peligro detectado por Agent_02_Hazard_Identifier"""
    id: str
    clasificacion: ClasificacionPeligro
    descripcion: str
    fuente: Optional[str] = None
    medio: Optional[str] = None
    individuo: Optional[str] = None
    
    # Contexto
    proceso: str
    zona_lugar: Optional[str] = None
    actividad: str
    tarea: str
    tipo_tarea: TipoTarea
    
    # Metadata
    confianza: float = Field(ge=0.0, le=1.0, default=0.8)

class RiesgoMapeado(BaseModel):
    """Riesgo asociado por Agent_03_Risk_Mapper"""
    peligro_id: str
    descripcion_riesgo: str
    efectos_posibles: List[str] = Field(default_factory=list)
    peor_consecuencia: str
    personas_expuestas: int = 1

class ControlExistente(BaseModel):
    """Control que ya tiene la empresa"""
    jerarquia: JerarquiaControl
    descripcion: str
    efectividad: Optional[str] = None  # "Alta", "Media", "Baja"

class ControlPropuesto(BaseModel):
    """Control sugerido por Agent_04_Control_Planner"""
    jerarquia: JerarquiaControl
    descripcion: str
    justificacion: str
    prioridad: int = Field(ge=1, le=5)
    costo_estimado: Optional[str] = None  # "Alto", "Medio", "Bajo"
    plazo_implementacion: Optional[str] = None  # "Inmediato", "Corto", etc.