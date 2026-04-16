"""
Clase base abstracta para todos los agentes
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Clase base para todos los agentes del sistema.
    
    Cada agente debe implementar:
    - execute(): Lógica principal del agente
    - validate_input(): Validación de entrada
    """
    
    def __init__(self, llm=None, **kwargs):
        """
        Args:
            llm: Modelo de lenguaje (opcional para agentes sin LLM)
            **kwargs: Configuración adicional del agente
        """
        self.llm = llm
        self.config = kwargs
        self.name = self.__class__.__name__
        logger.info(f"Inicializando agente: {self.name}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la lógica principal del agente.
        
        Args:
            input_data: Datos de entrada del agente
            
        Returns:
            Resultado del procesamiento
            
        Raises:
            Exception: Si ocurre un error durante la ejecución
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida que la entrada del agente sea correcta.
        
        Args:
            input_data: Datos a validar
            
        Returns:
            True si la entrada es válida
            
        Raises:
            ValueError: Si la entrada es inválida
        """
        pass
    
    def log_execution(self, stage: str, **kwargs):
        """Log estructurado de ejecución del agente"""
        logger.info(
            f"{self.name}.{stage}",
            agent=self.name,
            stage=stage,
            **kwargs
        )
