"""AgentState - Estado compartido entre agentes

Este modelo define la estructura que viaja por el grafo LangGraph.
Cada agente lee y actualiza este estado de forma inmutable.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional

from types.base_types import TaskStatus, DocumentoIngesta
from types.bronze_types import TextoExtraido
from types.silver_types import PeligroIdentificado
from types.gold_types import RiesgoCompleto

class AgentState(BaseModel):
    """Estado global que viaja por el grafo de agentes
    
    Este es el modelo central que define la comunicación entre nodos.
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
