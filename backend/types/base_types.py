"""Tipos y modelos base del sistema

Define las estructuras de datos fundamentales usando Pydantic
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TaskStatus(str, Enum):
    """Estados posibles de una tarea"""
    PENDING = "pending"
    EXTRACTING = "extracting"
    IDENTIFYING_HAZARDS = "identifying_hazards"
    MAPPING_RISKS = "mapping_risks"
    PLANNING_CONTROLS = "planning_controls"
    CALCULATING = "calculating"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"

class TipoTarea(str, Enum):
    """Tipo de tarea según GTC 45"""
    RUTINARIA = "Rutinaria"
    NO_RUTINARIA = "No Rutinaria"

class ClasificacionPeligro(str, Enum):
    """Clasificación de peligros según GTC 45:2012"""
    FISICO = "Físico"
    QUIMICO = "Químico"
    BIOLOGICO = "Biológico"
    BIOMECANICO = "Biomecánico"
    PSICOSOCIAL = "Psicosocial"
    CONDICIONES_SEGURIDAD = "Condiciones de Seguridad"
    FENOMENOS_NATURALES = "Fenómenos Naturales"

class JerarquiaControl(str, Enum):
    """Jerarquía de controles GTC 45"""
    ELIMINACION = "Eliminación"
    SUSTITUCION = "Sustitución"
    INGENIERIA = "Controles de Ingeniería"
    ADMINISTRATIVO = "Controles Administrativos/Señalización"
    EPP = "Equipos de Protección Personal (EPP)"

class DocumentoIngesta(BaseModel):
    """Documento cargado por el usuario"""
    document_id: str
    filename: str
    content_type: str
    storage_path: str
    empresa: str
    fecha_carga: datetime = Field(default_factory=datetime.utcnow)