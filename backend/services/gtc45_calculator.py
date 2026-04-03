from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def calcular_np(nd: int, ne: int) -> Tuple[int, str]:
    """Calcula Nivel de Probabilidad = ND x NE"""
    np = nd * ne
    
    if np >= 24:
        nivel = "Muy Alto"
    elif np >= 10:
        nivel = "Alto"
    elif np >= 6:
        nivel = "Medio"
    else:
        nivel = "Bajo"
    
    return np, nivel

def calcular_nr(np: int, nc: int) -> Tuple[int, str, str, str]:
    """Calcula Nivel de Riesgo = NP x NC y determina interpretación"""
    nr = np * nc
    
    # Interpretación según GTC 45
    if nr >= 600:
        interpretacion = "I"
        texto = "Situación crítica. Suspender actividades hasta que el riesgo esté bajo control."
        aceptabilidad = "No Aceptable"
    elif nr >= 150:
        interpretacion = "II"
        texto = "Corregir y adoptar medidas de control de inmediato."
        aceptabilidad = "No Aceptable"
    elif nr >= 40:
        interpretacion = "III"
        texto = "Mejorar si es posible. Sería conveniente justificar la intervención y su rentabilidad."
        aceptabilidad = "Aceptable con control"
    else:
        interpretacion = "IV"
        texto = "Mantener las medidas de control existentes."
        aceptabilidad = "Aceptable"
    
    return nr, interpretacion, texto, aceptabilidad

def obtener_nivel_nd(valor: int) -> str:
    """Obtiene el nivel textual del Nivel de Deficiencia"""
    niveles = {
        10: "Muy Alto",
        6: "Alto",
        2: "Medio"
    }
    return niveles.get(valor, "Bajo")

def obtener_nivel_ne(valor: int) -> str:
    """Obtiene el nivel textual del Nivel de Exposición"""
    niveles = {
        4: "Continua",
        3: "Frecuente",
        2: "Ocasional",
        1: "Esporádica"
    }
    return niveles.get(valor, "Esporádica")

def obtener_nivel_nc(valor: int) -> str:
    """Obtiene el nivel textual del Nivel de Consecuencia"""
    niveles = {
        100: "Mortal o Catastrófico",
        60: "Muy Grave",
        25: "Grave",
        10: "Leve"
    }
    return niveles.get(valor, "Leve")

def obtener_color_riesgo(interpretacion: str) -> str:
    """Obtiene el color semáforo según la interpretación del riesgo"""
    colores = {
        "I": "#DC2626",  # Rojo
        "II": "#EA580C",  # Naranja
        "III": "#EAB308",  # Amarillo
        "IV": "#16A34A"   # Verde
    }
    return colores.get(interpretacion, "#71717A")