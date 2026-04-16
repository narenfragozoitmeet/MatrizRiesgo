"""API v1 - SST Risk Matrix (con Agentes LangChain)"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import uuid
import logging
import structlog
from datetime import datetime, timezone

from db.mongodb import get_mongodb
from agents.chain import MatrizProcessingChain
from services.excel_generator import excel_generator
from models.matrices import MatrizResumen, TipoMatriz
from shared.validators import DocumentValidator
from shared.exceptions import (
    ValidationError,
    DocumentExtractionError,
    LLMProcessingError,
    MatrizNotFoundError
)
from api.security_middleware import limiter
from core.config import settings
from core.security import get_current_user, get_current_user_optional

logger = structlog.get_logger()
router = APIRouter()

# Inicializar cadena de procesamiento (singleton)
processing_chain = None

def get_processing_chain() -> MatrizProcessingChain:
    """Obtiene la instancia de la cadena de procesamiento"""
    global processing_chain
    if processing_chain is None:
        processing_chain = MatrizProcessingChain()
    return processing_chain

# ============================================
# MODELS
# ============================================

class IngestResponse(BaseModel):
    success: bool
    message: str
    matriz_id: str
    empresa: str

class MatrizResponse(BaseModel):
    id: str
    empresa: str
    documento_origen: str
    total_riesgos: int
    riesgos_criticos: int
    riesgos_altos: int
    riesgos_medios: int
    riesgos_bajos: int
    created_at: str
    metodologia: str

class InfoRequisitoResponse(BaseModel):
    title: str
    description: str
    document_types: List[dict]
    required_info: List[str]
    estructura_ejemplo: dict

# ============================================
# ENDPOINTS
# ============================================

@router.get("/info-requisitos", response_model=InfoRequisitoResponse)
async def get_info_requisitos():
    """Información sobre documentos requeridos"""
    return InfoRequisitoResponse(
        title="Información Requerida para Matriz de Riesgos SST",
        description="El sistema analiza documentos de tu empresa para identificar peligros y valorar riesgos laborales según la metodología GTC 45 (Guía Técnica Colombiana) combinada con RAM (Risk Assessment Matrix).",
        document_types=[
            {
                "tipo": "PDF",
                "descripcion": "Informes de seguridad, evaluaciones de riesgos, procedimientos operativos",
                "ejemplos": ["Informe SST anual", "Manual de procedimientos", "Evaluación de riesgos"]
            },
            {
                "tipo": "Word (.docx)",
                "descripcion": "Documentos corporativos, políticas, descripciones de procesos",
                "ejemplos": ["Política SST", "Descripción de procesos", "Informes internos"]
            },
            {
                "tipo": "Excel (.xlsx)",
                "descripcion": "Inventarios de actividades, listados de equipos, registros",
                "ejemplos": ["Inventario de maquinaria", "Listado de actividades", "Registro de incidentes"]
            }
        ],
        required_info=[
            "✅ Nombre de la empresa (debe aparecer en el documento)",
            "✅ Descripción de procesos y actividades laborales",
            "✅ Áreas o zonas de trabajo",
            "✅ Equipos, maquinaria o herramientas utilizadas",
            "✅ Sustancias químicas manejadas (si aplica)",
            "✅ Condiciones de trabajo (ruido, temperatura, iluminación, etc.)",
            "✅ Cualquier peligro o riesgo ya identificado"
        ],
        estructura_ejemplo={
            "seccion_1": {
                "titulo": "Identificación de la Empresa",
                "contenido": "EMPRESA: Constructora ACME S.A."
            },
            "seccion_2": {
                "titulo": "Descripción de Actividades",
                "contenido": "Proceso: Construcción | Actividad: Trabajos en altura | Zona: Obra edificio piso 5"
            },
            "seccion_3": {
                "titulo": "Peligros/Riesgos Observados",
                "contenido": "Exposición a ruido de maquinaria, manipulación manual de cargas, uso de herramientas eléctricas"
            }
        }
    )


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def ingest_and_generate_matrix(
    request: Request,  # Requerido por slowapi
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_optional)  # Auth opcional
):
    """
    Ingesta documento y genera matriz de riesgos SST
    
    SEGURIDAD:
    - Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minuto
    - Tamaño máximo: {MAX_FILE_SIZE_MB}MB
    - Validación de tipo de archivo
    - Sanitización de texto
    - Auth opcional (si está autenticado, se asocia al usuario)
    
    Args:
        file: Documento PDF, Word o Excel
        current_user: Usuario autenticado (opcional)
    
    Returns:
        Matriz generada con ID y empresa detectada
    """
    document_id = str(uuid.uuid4())
    user_id = current_user["sub"] if current_user else None
    
    try:
        # 1. Leer archivo
        file_data = await file.read()
        
        logger.info(
            "ingest_started",
            document_id=document_id,
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(file_data)
        )
        
        # 2. Validar archivo
        DocumentValidator.validate_file(
            filename=file.filename,
            content_type=file.content_type,
            file_size=len(file_data)
        )
        
        # 3. Determinar tipo de archivo
        file_type = None
        if file.content_type == "application/pdf":
            file_type = "pdf"
        elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            file_type = "docx"
        elif file.content_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            file_type = "xlsx"
        else:
            raise ValidationError("Tipo de archivo no soportado")
        
        # 4. Procesar documento con cadena de agentes LangChain
        logger.info("processing_with_agents", file_type=file_type)
        
        chain = get_processing_chain()
        matriz_data = await chain.process_document(
            file_data=file_data,
            filename=file.filename,
            file_type=file_type
        )
        
        # 5. Agregar user_id si está autenticado
        matriz_data["user_id"] = user_id
        
        # 6. Guardar en MongoDB
        mongodb = get_mongodb()
        matriz_id = str(uuid.uuid4())
        matriz_data["_id"] = matriz_id
        
        mongodb.matrices_sst.insert_one(matriz_data)
        
        logger.info(
            "matriz_generated",
            matriz_id=matriz_id,
            empresa=matriz_data["empresa"],
            total_riesgos=matriz_data["total_riesgos"],
            riesgos_criticos=matriz_data["riesgos_criticos"]
        )
        
        return IngestResponse(
            success=True,
            message=f"Matriz SST generada exitosamente para {matriz_data['empresa']}",
            matriz_id=matriz_id,
            empresa=matriz_data["empresa"]
        )
        
    except (ValidationError, DocumentExtractionError, LLMProcessingError) as e:
        logger.warning(
            "ingest_validation_error",
            document_id=document_id,
            error_detail=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "ingest_unexpected_error",
            document_id=document_id,
            error_detail=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")


@router.get("/matrix/{matriz_id}", response_model=MatrizResponse)
async def get_matriz(matriz_id: str):
    """Obtiene una matriz SST por ID"""
    try:
        mongodb = get_mongodb()
        matriz_data = mongodb.matrices_sst.find_one({"_id": matriz_id})
        
        if not matriz_data:
            raise MatrizNotFoundError(f"Matriz {matriz_id} no encontrada")
        
        logger.info("matriz_retrieved", matriz_id=matriz_id)
        
        return MatrizResponse(
            id=matriz_id,
            empresa=matriz_data["empresa"],
            documento_origen=matriz_data["documento_origen"],
            total_riesgos=matriz_data["total_riesgos"],
            riesgos_criticos=matriz_data["riesgos_criticos"],
            riesgos_altos=matriz_data["riesgos_altos"],
            riesgos_medios=matriz_data["riesgos_medios"],
            riesgos_bajos=matriz_data["riesgos_bajos"],
            created_at=matriz_data["created_at"].isoformat(),
            metodologia=matriz_data["metodologia"]
        )
    except MatrizNotFoundError:
        raise
    except Exception as e:
        logger.error("get_matriz_error", matriz_id=matriz_id, error_detail=str(e))
        raise HTTPException(status_code=500, detail="Error obteniendo matriz")


@router.get("/matrix/{matriz_id}/export")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE * 2}/minute")  # Mayor límite para exports
async def export_matriz(request: Request, matriz_id: str):
    """
    Exporta matriz SST a Excel
    
    Args:
        matriz_id: ID de la matriz
    
    Returns:
        Archivo Excel (.xlsx)
    """
    try:
        mongodb = get_mongodb()
        from models.matrices import MatrizSST
        
        matriz_data = mongodb.matrices_sst.find_one({"_id": matriz_id})
        
        if not matriz_data:
            raise MatrizNotFoundError(f"Matriz {matriz_id} no encontrada")
        
        matriz = MatrizSST(**matriz_data)
        excel_data = excel_generator.generar_matriz_sst(matriz)
        filename = f"matriz_sst_{matriz.empresa.replace(' ', '_')}_{matriz_id[:8]}.xlsx"
        
        logger.info("matriz_exported", matriz_id=matriz_id, empresa=matriz.empresa)
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except MatrizNotFoundError:
        raise
    except Exception as e:
        logger.error("export_error", matriz_id=matriz_id, error=str(e))
        raise HTTPException(status_code=500, detail="Error exportando matriz")


@router.get("/matrices", response_model=List[MatrizResumen])
async def list_matrices(
    request: Request,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Lista todas las matrices SST generadas
    
    Si el usuario está autenticado, retorna solo sus matrices.
    Si no está autenticado, retorna todas.
    
    Returns:
        Lista de matrices (máx 100, ordenadas por fecha)
    """
    try:
        mongodb = get_mongodb()
        matrices = []
        
        # Filtrar por usuario si está autenticado
        query = {}
        if current_user:
            query["user_id"] = current_user["sub"]
        
        sst_matrices = mongodb.matrices_sst.find(query).sort("created_at", -1).limit(100)
        for m in sst_matrices:
            matrices.append(MatrizResumen(
                id=m["_id"],
                tipo_matriz=TipoMatriz.SST,
                empresa=m["empresa"],
                documento_origen=m["documento_origen"],
                total_riesgos=m["total_riesgos"],
                riesgos_criticos=m["riesgos_criticos"],
                created_at=m["created_at"],
                estado=m["estado"]
            ))
        
        logger.info("matrices_listed", count=len(matrices))
        return matrices
    except Exception as e:
        logger.error("list_matrices_error", error_detail=str(e))
        raise HTTPException(status_code=500, detail="Error listando matrices")
