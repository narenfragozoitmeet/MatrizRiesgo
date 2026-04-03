"""AgentState - Estado compartido entre todos los agentes del grafo LangGraph

Este modelo Pydantic define la estructura de datos que viaja entre nodos.
Cada agente lee y actualiza este estado de forma inmutable.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
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
    RUTINARIA = "Rutinaria"
    NO_RUTINARIA = "No Rutinaria"

class ClasificacionPeligro(str, Enum):
    FISICO = "Físico"
    QUIMICO = "Químico"
    BIOLOGICO = "Biológico"
    BIOMECANICO = "Biomecánico"
    PSICOSOCIAL = "Psicosocial"
    CONDICIONES_SEGURIDAD = "Condiciones de Seguridad"
    FENOMENOS_NATURALES = "Fenómenos Naturales"

class JerarquiaControl(str, Enum):
    ELIMINACION = "Eliminación"
    SUSTITUCION = "Sustitución"
    INGENIERIA = "Controles de Ingeniería"
    ADMINISTRATIVO = "Controles Administrativos/Señalización"
    EPP = "Equipos de Protección Personal (EPP)"

# ==================== Modelos de datos ====================

class DocumentoIngesta(BaseModel):
    """Datos del documento cargado"""
    document_id: str
    filename: str
    content_type: str
    storage_path: str
    empresa: str
    fecha_carga: datetime = Field(default_factory=datetime.utcnow)

class TextoExtraido(BaseModel):
    """Resultado del Agent_Extractor (Bronze)"""
    texto_crudo: str
    texto_limpio: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    num_paginas: Optional[int] = None
    num_palabras: Optional[int] = None

class PeligroIdentificado(BaseModel):
    """Peligro detectado por Agent_Hazard_ID (Silver)"""
    id: str
    clasificacion: ClasificacionPeligro
    descripcion: str
    fuente: Optional[str] = None
    medio: Optional[str] = None
    individuo: Optional[str] = None
    proceso: str
    zona_lugar: Optional[str] = None
    actividad: str
    tarea: str
    tipo_tarea: TipoTarea
    confianza: float = Field(ge=0.0, le=1.0, default=0.8)

class RiesgoMapeado(BaseModel):
    """Riesgo asociado al peligro por Agent_Risk_Mapper (Silver)"""
    peligro_id: str
    descripcion_riesgo: str
    efectos_posibles: List[str] = Field(default_factory=list)
    peor_consecuencia: str
    personas_expuestas: int = 1

class ControlExistente(BaseModel):
    """Control actual identificado"""
    jerarquia: JerarquiaControl
    descripcion: str
    efectividad: Optional[str] = None  # "Alta", "Media", "Baja"

class ControlPropuesto(BaseModel):
    """Control sugerido por Agent_Control_Planner"""
    jerarquia: JerarquiaControl
    descripcion: str
    justificacion: str
    prioridad: int = Field(ge=1, le=5)
    costo_estimado: Optional[str] = None
    plazo_implementacion: Optional[str] = None

class ValoracionGTC45(BaseModel):
    """Resultado del Node_Calculator (determinista)"""
    # Inputs
    nd_valor: int  # 10, 6, 2
    ne_valor: int  # 4, 3, 2, 1
    nc_valor: int  # 100, 60, 25, 10
    
    # Outputs calculados
    np_valor: int
    np_nivel: str
    nr_valor: int
    interpretacion: str  # I, II, III, IV
    interpretacion_texto: str
    aceptabilidad: str  # "Aceptable", "No Aceptable", etc.

class MatrizRAM(BaseModel):
    """Valoración RAM (si aplica)"""
    probabilidad: str  # A, B, C, D, E
    gravedad_personas: int  # 0-5
    gravedad_economica: int  # 0-5
    gravedad_ambiental: int  # 0-5
    gravedad_clientes: int  # 0-5
    gravedad_reputacion: int  # 0-5
    nivel_riesgo: str

class RiesgoCompleto(BaseModel):
    """Estructura completa de un riesgo (Gold)"""
    id: str
    peligro: PeligroIdentificado
    riesgo: RiesgoMapeado
    controles_existentes: List[ControlExistente] = Field(default_factory=list)
    controles_propuestos: List[ControlPropuesto] = Field(default_factory=list)
    valoracion_gtc45: ValoracionGTC45
    valoracion_ram: Optional[MatrizRAM] = None

# ==================== AgentState Principal ====================

class AgentState(BaseModel):
    """Estado global que viaja por el grafo de agentes
    
    Este es el modelo central que define la comunicación entre nodos.
    Cada agente recibe este estado, lo procesa y retorna una versión actualizada.
    """
    
    # Metadatos de la tarea
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Documento original
    documento: DocumentoIngesta
    
    # Resultados de cada agente (se van poblando)
    texto_extraido: Optional[TextoExtraido] = None
    peligros_identificados: List[PeligroIdentificado] = Field(default_factory=list)
    riesgos_completos: List[RiesgoCompleto] = Field(default_factory=list)
    
    # Resultado final
    matriz_id_gold: Optional[str] = None
    
    # Errores y logs
    errors: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    
    # Configuración
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_log(self, message: str):
        """Añade un log al estado"""
        self.logs.append(f"[{datetime.utcnow().isoformat()}] {message}")
        self.updated_at = datetime.utcnow()
    
    def add_error(self, error: str):
        """Añade un error al estado"""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.utcnow()
    
    def update_status(self, new_status: TaskStatus):
        """Actualiza el estado de la tarea"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        self.add_log(f"Estado actualizado a: {new_status.value}")