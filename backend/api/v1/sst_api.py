"""API v1 - SST Risk Matrix Generation Endpoint

Generación automática de Matrices de Riesgos SST (GTC 45 + RAM)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
import uuid
import logging
from datetime import datetime

from db.mongodb import get_mongodb
from services.document_extractor import document_extractor
from services.matriz_sst_processor import matriz_sst_processor
from services.excel_generator import excel_generator
from models.matrices import MatrizResumen, TipoMatriz

logger = logging.getLogger(__name__)
router = APIRouter()

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
    """Información sobre requisitos de documentos"""
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
    """
    Devuelve información sobre qué documentos necesita el sistema y su estructura
    
    Este endpoint se usa para el ícono (!) informativo en el frontend
    """
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
async def ingest_and_generate_matrix(
    file: UploadFile = File(...)
):
    """
    Ingesta documento y genera matriz de riesgos SST
    
    El nombre de la empresa se extrae AUTOMÁTICAMENTE del documento
    
    Flujo:
    1. Upload documento (PDF/Word/Excel)
    2. Extracción de texto
    3. Extracción automática del nombre de empresa
    4. Procesamiento con agentes LLM (Gemini 2.5 Flash)
    5. Evaluación con GTC 45 + RAM
    6. Generación de matriz completa
    7. Guardado en MongoDB
    
    Args:
        file: Documento PDF, Word o Excel con información de la empresa
    
    Returns:
        ID de la matriz generada y nombre de empresa detectado
    """
    try:
        # Validar tipo de archivo
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no soportado. Use PDF, Word (.docx) o Excel (.xlsx)"
            )
        
        logger.info(f"📥 Ingesta iniciada: {file.filename}")
        
        # 1. Leer archivo
        file_data = await file.read()
        document_id = str(uuid.uuid4())
        
        # 2. Extracción de texto
        logger.info("📄 Extrayendo texto del documento...")
        texto_extraido, tipo_doc = document_extractor.extract(
            file_data, file.filename, file.content_type
        )
        
        if not texto_extraido or len(texto_extraido) < 100:
            raise HTTPException(
                status_code=400,
                detail="El documento no contiene suficiente texto para analizar. Asegúrate de que el documento tenga información sobre la empresa y sus actividades."
            )
        
        # 3. Procesamiento SST (incluye extracción de nombre empresa)
        logger.info("🔄 Procesando matriz SST con GTC 45 + RAM...")
        matriz = await matriz_sst_processor.procesar(
            texto_documento=texto_extraido,
            nombre_documento=file.filename,
            document_id=document_id
        )
        
        # 4. Guardar documento original (Bronze)
        mongodb = get_mongodb()
        bronze_doc = {
            "_id": document_id,
            "empresa": matriz.empresa,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(file_data),
            "created_at": datetime.now()
        }
        mongodb.documentos_bronze.insert_one(bronze_doc)
        logger.info(f"✅ Documento guardado en Bronze: {document_id}")
        
        # 5. Guardar matriz en MongoDB
        matriz_id = str(uuid.uuid4())
        matriz_dict = matriz.model_dump()
        matriz_dict["_id"] = matriz_id
        mongodb.matrices_sst.insert_one(matriz_dict)
        
        logger.info(f"✅ Matriz SST generada: {matriz_id} | Empresa: {matriz.empresa}")
        
        return IngestResponse(
            success=True,
            message=f"Matriz SST generada exitosamente para {matriz.empresa}",
            matriz_id=matriz_id,
            empresa=matriz.empresa
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en ingesta: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix/{matriz_id}", response_model=MatrizResponse)
async def get_matriz(matriz_id: str):
    """
    Obtiene una matriz SST por ID
    
    Args:
        matriz_id: ID de la matriz
    """
    try:
        mongodb = get_mongodb()
        matriz_data = mongodb.matrices_sst.find_one({"_id": matriz_id})
        
        if not matriz_data:
            raise HTTPException(status_code=404, detail="Matriz no encontrada")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo matriz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix/{matriz_id}/export")
async def export_matriz(matriz_id: str):
    """
    Exporta matriz SST a Excel con formato GTC 45
    
    Args:
        matriz_id: ID de la matriz
    
    Returns:
        Archivo Excel (.xlsx) con matriz completa
    """
    try:
        mongodb = get_mongodb()
        
        # Obtener matriz de MongoDB
        from models.matrices import MatrizSST
        matriz_data = mongodb.matrices_sst.find_one({"_id": matriz_id})
        
        if not matriz_data:
            raise HTTPException(status_code=404, detail="Matriz no encontrada")
        
        matriz = MatrizSST(**matriz_data)
        excel_data = excel_generator.generar_matriz_sst(matriz)
        filename = f"matriz_sst_{matriz.empresa.replace(' ', '_')}_{matriz_id[:8]}.xlsx"
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exportando matriz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrices", response_model=List[MatrizResumen])
async def list_matrices():
    """
    Lista todas las matrices SST generadas
    
    Returns:
        Lista de matrices ordenadas por fecha (más recientes primero)
    """
    try:
        mongodb = get_mongodb()
        matrices = []
        
        sst_matrices = mongodb.matrices_sst.find().sort("created_at", -1).limit(100)
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
        
        return matrices
        
    except Exception as e:
        logger.error(f"Error listando matrices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
