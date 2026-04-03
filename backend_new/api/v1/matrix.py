"""API v1 - Matrix Endpoint

POST /api/v1/matrix - Generación manual de matriz
GET /api/v1/matrix/{id} - Obtener matriz por ID
GET /api/v1/matrix/{id}/export - Descargar Excel
GET /api/v1/matrices - Listar todas las matrices
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from db.session import get_db
from db.schemas.gold import MatrizGTC45
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class MatrizResponse(BaseModel):
    id: str
    nombre_empresa: str
    documento_origen: str
    total_riesgos: int
    riesgos_criticos: int
    riesgos_altos: int
    riesgos_medios: int
    riesgos_bajos: int
    fecha_elaboracion: str
    estado: str

@router.get("/matrix/{matriz_id}", response_model=MatrizResponse)
async def get_matriz(matriz_id: str, db: Session = Depends(get_db)):
    """Obtiene una matriz GTC 45 por ID
    
    Args:
        matriz_id: ID de la matriz en esquema Gold
        
    Returns:
        Datos completos de la matriz
    """
    try:
        matriz = db.query(MatrizGTC45).filter(MatrizGTC45.id == matriz_id).first()
        
        if not matriz:
            raise HTTPException(status_code=404, detail="Matriz no encontrada")
        
        return MatrizResponse(
            id=matriz.id,
            nombre_empresa=matriz.nombre_empresa,
            documento_origen=matriz.documento_origen,
            total_riesgos=matriz.total_riesgos,
            riesgos_criticos=matriz.riesgos_criticos,
            riesgos_altos=matriz.riesgos_altos,
            riesgos_medios=matriz.riesgos_medios,
            riesgos_bajos=matriz.riesgos_bajos,
            fecha_elaboracion=matriz.fecha_elaboracion.isoformat(),
            estado=matriz.estado
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo matriz {matriz_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matrix/{matriz_id}/export")
async def export_matriz_excel(matriz_id: str, db: Session = Depends(get_db)):
    """Descarga matriz en formato Excel GTC 45
    
    Args:
        matriz_id: ID de la matriz
        
    Returns:
        Archivo Excel (.xlsx)
    """
    try:
        matriz = db.query(MatrizGTC45).filter(MatrizGTC45.id == matriz_id).first()
        
        if not matriz:
            raise HTTPException(status_code=404, detail="Matriz no encontrada")
        
        # TODO: Implementar generación de Excel
        # from services.excel_generator_gtc45 import generate_excel
        # excel_data = generate_excel(matriz)
        
        excel_data = b""  # Placeholder
        
        filename = f"matriz_gtc45_{matriz.nombre_empresa}_{matriz_id[:8]}.xlsx"
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exportando matriz {matriz_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matrices", response_model=List[MatrizResponse])
async def list_matrices(db: Session = Depends(get_db)):
    """Lista todas las matrices generadas
    
    Returns:
        Lista de matrices con información resumida
    """
    try:
        matrices = db.query(MatrizGTC45).order_by(MatrizGTC45.fecha_elaboracion.desc()).limit(100).all()
        
        return [
            MatrizResponse(
                id=m.id,
                nombre_empresa=m.nombre_empresa,
                documento_origen=m.documento_origen,
                total_riesgos=m.total_riesgos,
                riesgos_criticos=m.riesgos_criticos,
                riesgos_altos=m.riesgos_altos,
                riesgos_medios=m.riesgos_medios,
                riesgos_bajos=m.riesgos_bajos,
                fecha_elaboracion=m.fecha_elaboracion.isoformat(),
                estado=m.estado
            )
            for m in matrices
        ]
        
    except Exception as e:
        logger.error(f"Error listando matrices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))