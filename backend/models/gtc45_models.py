from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Proceso(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class Actividad(BaseModel):
    nombre: str
    tipo: str  # "Rutinaria" o "No Rutinaria"
    proceso: str

class Tarea(BaseModel):
    nombre: str
    descripcion: str
    actividad: str

class Peligro(BaseModel):
    clasificacion: str  # Físico, Químico, Biológico, Biomecánico, Psicosocial, Condiciones de Seguridad, Fenómenos Naturales
    descripcion: str
    fuente: Optional[str] = None
    efectos_posibles: List[str] = Field(default_factory=list)

class ValoracionGTC45(BaseModel):
    # Nivel de Deficiencia
    nd_valor: int  # 10, 6, 2
    nd_nivel: str  # "Muy Alto", "Alto", "Medio", "Bajo"
    nd_justificacion: str
    
    # Nivel de Exposición
    ne_valor: int  # 4, 3, 2, 1
    ne_nivel: str  # "Continua", "Frecuente", "Ocasional", "Esporádica"
    ne_justificacion: str
    
    # Nivel de Probabilidad (ND x NE)
    np_valor: int
    np_nivel: str  # "Muy Alto", "Alto", "Medio", "Bajo"
    
    # Nivel de Consecuencia
    nc_valor: int  # 100, 60, 25, 10
    nc_nivel: str  # "Mortal", "Muy Grave", "Grave", "Leve"
    nc_justificacion: str
    
    # Nivel de Riesgo (NP x NC)
    nr_valor: int
    
    # Interpretación del Riesgo
    interpretacion: str  # "I", "II", "III", "IV"
    interpretacion_texto: str  # "No aceptable", "Mejorar si es posible", etc.
    aceptabilidad: str  # "Aceptable", "No Aceptable"

class Control(BaseModel):
    jerarquia: str  # "Eliminación", "Sustitución", "Ingeniería", "Administrativo", "EPP"
    descripcion: str
    responsable: Optional[str] = None
    fecha_implementacion: Optional[str] = None

class RiesgoGTC45(BaseModel):
    id: str
    proceso: Proceso
    actividad: Actividad
    tarea: Tarea
    peligro: Peligro
    valoracion: ValoracionGTC45
    controles_existentes: List[Control] = Field(default_factory=list)
    controles_recomendados: List[Control] = Field(default_factory=list)
    
class MatrizGTC45(BaseModel):
    id: str
    nombre_empresa: str
    documento_origen: str
    fecha_elaboracion: str
    responsable_elaboracion: str
    fecha_actualizacion: Optional[str] = None
    riesgos: List[RiesgoGTC45]
    resumen_ejecutivo: str
    estadisticas: dict
    created_at: str