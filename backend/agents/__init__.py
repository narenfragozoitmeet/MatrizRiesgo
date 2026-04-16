"""
Sistema de Agentes con LangChain para procesamiento de documentos SST
"""

from .base import BaseAgent
from .extractor import DocumentExtractorAgent
from .analyzer import HazardAnalyzerAgent
from .calculator import RiskCalculatorAgent
from .chain import MatrizProcessingChain

__all__ = [
    'BaseAgent',
    'DocumentExtractorAgent',
    'HazardAnalyzerAgent',
    'RiskCalculatorAgent',
    'MatrizProcessingChain'
]
