"""Tipos para el esquema Gold (datos finales)"""

from pydantic import BaseModel, Field
from typing import List, Optional
from types.silver_types import PeligroIdentificado, RiesgoMapeado, ControlExistente, ControlPropuesto

class ValoracionGTC45(BaseModel):
    """Valoración calculada por Node_05_Calculator"""
    # Inputs
    nd_valor: int  # 10, 6, 2
    ne_valor: int  # 4, 3, 2, 1
    nc_valor: int  # 100, 60, 25, 10
    
    # Outputs calculados (determinísticos)
    np_valor: int  # ND x NE
    np_nivel: str  # "Muy Alto", "Alto", "Medio", "Bajo"
    nr_valor: int  # NP x NC
    interpretacion: str  # "I", "II", "III", "IV"
    interpretacion_texto: str
    aceptabilidad: str  # "Aceptable", "No Aceptable"

class MatrizRAM(BaseModel):
    """Valoración RAM (opcional)"""
    probabilidad: str  # A, B, C, D, E
    gravedad_personas: int  # 0-5
    gravedad_economica: int  # 0-5
    gravedad_ambiental: int  # 0-5
    gravedad_clientes: int  # 0-5
    gravedad_reputacion: int  # 0-5
    nivel_riesgo: str

class RiesgoCompleto(BaseModel):
    """Riesgo completo con toda su información (Gold)"""
    id: str
    peligro: PeligroIdentificado
    riesgo: RiesgoMapeado
    controles_existentes: List[ControlExistente] = Field(default_factory=list)
    controles_propuestos: List[ControlPropuesto] = Field(default_factory=list)
    valoracion_gtc45: ValoracionGTC45
    valoracion_ram: Optional[MatrizRAM] = None