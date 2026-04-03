"""Node 05 - Calculator (Determinístico)

Responsabilidad:
- Ejecutar cálculos matemáticos puros (NO IA)
- Fórmulas GTC 45: NP = ND x NE, NR = NP x NC
- Cruzar matriz RAM
- 0% alucinaciones garantizado
"""

import logging
from graphs.state import AgentState
from types.base_types import TaskStatus
from types.gold_types import ValoracionGTC45

logger = logging.getLogger(__name__)

class Node05Calculator:
    """Nodo 05 - Calculador determinístico (sin IA)"""
    
    def __init__(self):
        self.name = "Node_05_Calculator"
    
    def calcular_np(self, nd: int, ne: int) -> tuple[int, str]:
        """Calcula Nivel de Probabilidad = ND x NE
        
        Args:
            nd: Nivel de Deficiencia (10, 6, 2)
            ne: Nivel de Exposición (4, 3, 2, 1)
            
        Returns:
            (np_valor, np_nivel)
        """
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
    
    def calcular_nr(self, np: int, nc: int) -> tuple[int, str, str, str]:
        """Calcula Nivel de Riesgo = NP x NC
        
        Args:
            np: Nivel de Probabilidad
            nc: Nivel de Consecuencia (100, 60, 25, 10)
            
        Returns:
            (nr_valor, interpretacion, texto, aceptabilidad)
        """
        nr = np * nc
        
        # Interpretación según GTC 45:2012
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
            texto = "Mejorar si es posible. Sería conveniente justificar la intervención."
            aceptabilidad = "Aceptable con control"
        else:
            interpretacion = "IV"
            texto = "Mantener las medidas de control existentes."
            aceptabilidad = "Aceptable"
        
        return nr, interpretacion, texto, aceptabilidad
    
    def obtener_nivel_nd(self, valor: int) -> str:
        """Obtiene nivel textual de ND"""
        niveles = {10: "Muy Alto", 6: "Alto", 2: "Medio"}
        return niveles.get(valor, "Bajo")
    
    def obtener_nivel_ne(self, valor: int) -> str:
        """Obtiene nivel textual de NE"""
        niveles = {4: "Continua", 3: "Frecuente", 2: "Ocasional", 1: "Esporádica"}
        return niveles.get(valor, "Esporádica")
    
    def obtener_nivel_nc(self, valor: int) -> str:
        """Obtiene nivel textual de NC"""
        niveles = {100: "Mortal o Catastrófico", 60: "Muy Grave", 25: "Grave", 10: "Leve"}
        return niveles.get(valor, "Leve")
    
    def execute(self, state: AgentState) -> AgentState:
        """Ejecuta cálculos determinísticos
        
        IMPORTANTE: Este nodo NO usa LLM, solo matemáticas puras
        
        Args:
            state: Estado con datos para calcular
            
        Returns:
            Estado con valoraciones calculadas
        """
        try:
            logger.info(f"[{state.task_id}] {self.name} iniciado")
            state.update_status(TaskStatus.CALCULATING)
            state.add_log(f"{self.name}: Calculando niveles de riesgo (GTC 45)...")
            
            # TODO: Obtener valores ND, NE, NC de los datos
            # Estos valores deben venir de los agentes anteriores o de análisis
            
            # Placeholder: valores de ejemplo
            nd_valor = 6  # Alto
            ne_valor = 3  # Frecuente
            nc_valor = 25  # Grave
            
            # Cálculos determinísticos
            np_valor, np_nivel = self.calcular_np(nd_valor, ne_valor)
            nr_valor, interpretacion, interpretacion_texto, aceptabilidad = self.calcular_nr(np_valor, nc_valor)
            
            # Crear valoración
            valoracion = ValoracionGTC45(
                nd_valor=nd_valor,
                ne_valor=ne_valor,
                nc_valor=nc_valor,
                np_valor=np_valor,
                np_nivel=np_nivel,
                nr_valor=nr_valor,
                interpretacion=interpretacion,
                interpretacion_texto=interpretacion_texto,
                aceptabilidad=aceptabilidad
            )
            
            state.add_log(f"{self.name}: Cálculos completados. NR={nr_valor} (Nivel {interpretacion})")
            
            # TODO: Asociar valoraciones a los riesgos en state
            
            return state
            
        except Exception as e:
            logger.error(f"[{state.task_id}] Error en {self.name}: {str(e)}")
            state.add_error(f"{self.name}: {str(e)}")
            return state

def node_05_calculator(state: AgentState) -> AgentState:
    """Nodo del grafo para Calculator"""
    calculator = Node05Calculator()
    return calculator.execute(state)