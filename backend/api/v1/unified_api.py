"""API v1 - Unified Ingest & Matrix Generation Endpoint"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
import uuid
import logging
from datetime import datetime

from db.mongodb import get_mongodb
from services.document_extractor import document_extractor
from services.matriz_sst_processor import matriz_sst_processor
from services.matriz_legal_processor import matriz_legal_processor
from services.excel_generator import excel_generator
from models.matrices import TipoMatriz, MatrizResumen

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# MODELS
# ============================================

class IngestResponse(BaseModel):
    success: bool
    message: str
    matriz_id: str
    tipo_matriz: TipoMatriz

class MatrizResponse(BaseModel):
    id: str
    tipo_matriz: TipoMatriz
    empresa: str
    documento_origen: str
    total_riesgos: int
    riesgos_criticos: int
    riesgos_altos: int
    riesgos_medios: int
    riesgos_bajos: int
    created_at: str
    metodologia: str

# ============================================
# ENDPOINTS
# ============================================

@router.post("/ingest", response_model=IngestResponse)
async def ingest_and_generate_matrix(
    file: UploadFile = File(...),
    empresa: str = Form(...),
    tipo_matriz: str = Form(...)  # "sst" o "legal"
):
    """
    Ingesta documento y genera matriz de riesgos
    
    Flujo:
    1. Upload documento (PDF/Word/Excel)
    2. Extracción de texto
    3. Procesamiento con agentes LLM
    4. Generación de matriz completa
    5. Guardado en MongoDB
    
    Args:
        file: Documento PDF, Word o Excel
        empresa: Nombre de la empresa
        tipo_matriz: "sst" (GTC 45) o "legal" (Riesgos Legales)
    
    Returns:
        ID de la matriz generada
    """
    try:
        # Validar tipo de matriz
        if tipo_matriz not in ["sst", "legal"]:
            raise HTTPException(
                status_code=400,
                detail="tipo_matriz debe ser 'sst' o 'legal'"
            )
        
        tipo_matriz_enum = TipoMatriz.SST if tipo_matriz == "sst" else TipoMatriz.LEGAL
        
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
                detail="Tipo de archivo no soportado. Use PDF, Word o Excel."
            )
        
        logger.info(f"📥 Ingesta iniciada: {empresa} | {tipo_matriz} | {file.filename}")
        
        # 1. Leer archivo
        file_data = await file.read()
        document_id = str(uuid.uuid4())
        
        # 2. Guardar documento original (Bronze)
        mongodb = get_mongodb()
        bronze_doc = {
            "_id": document_id,
            "empresa": empresa,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(file_data),
            "created_at": datetime.now()
        }
        mongodb.documentos_bronze.insert_one(bronze_doc)
        logger.info(f"✅ Documento guardado en Bronze: {document_id}")
        
        # 3. Extracción de texto
        logger.info("📄 Extrayendo texto del documento...")
        texto_extraido, tipo_doc = document_extractor.extract(
            file_data, file.filename, file.content_type
        )
        
        if not texto_extraido or len(texto_extraido) < 100:
            raise HTTPException(
                status_code=400,
                detail="El documento no contiene suficiente texto para analizar"
            )
        
        # 4. Procesamiento según tipo de matriz
        if tipo_matriz_enum == TipoMatriz.SST:
            logger.info("🔄 Procesando matriz SST (GTC 45)...")
            matriz = await matriz_sst_processor.procesar(
                texto_documento=texto_extraido,
                empresa=empresa,
                nombre_documento=file.filename,
                document_id=document_id
            )
            
            # Guardar en MongoDB
            matriz_id = str(uuid.uuid4())
            matriz_dict = matriz.model_dump()
            matriz_dict["_id"] = matriz_id
            mongodb.matrices_sst.insert_one(matriz_dict)
            
        else:  # LEGAL
            logger.info("🔄 Procesando matriz Legal...")
            matriz = await matriz_legal_processor.procesar(
                texto_documento=texto_extraido,
                empresa=empresa,
                nombre_documento=file.filename,
                document_id=document_id
            )
            
            # Guardar en MongoDB
            matriz_id = str(uuid.uuid4())
            matriz_dict = matriz.model_dump()
            matriz_dict["_id"] = matriz_id
            mongodb.matrices_legales.insert_one(matriz_dict)
        
        logger.info(f"✅ Matriz generada y guardada: {matriz_id}")
        
        return IngestResponse(
            success=True,
            message=f"Matriz {tipo_matriz.upper()} generada exitosamente",
            matriz_id=matriz_id,
            tipo_matriz=tipo_matriz_enum
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en ingesta: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix/{tipo}/{matriz_id}", response_model=MatrizResponse)
async def get_matriz(tipo: str, matriz_id: str):
    """
    Obtiene una matriz por ID
    
    Args:
        tipo: "sst" o "legal"
        matriz_id: ID de la matriz
    """
    try:
        mongodb = get_mongodb()
        
        if tipo == "sst":
            matriz_data = mongodb.matrices_sst.find_one({"_id": matriz_id})
        elif tipo == "legal":
            matriz_data = mongodb.matrices_legales.find_one({"_id": matriz_id})
        else:
            raise HTTPException(status_code=400, detail="tipo debe ser 'sst' o 'legal'")
        
        if not matriz_data:
            raise HTTPException(status_code=404, detail="Matriz no encontrada")
        
        return MatrizResponse(
            id=matriz_id,
            tipo_matriz=matriz_data["tipo_matriz"],
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


@router.get("/matrix/{tipo}/{matriz_id}/export")
async def export_matriz(tipo: str, matriz_id: str):
    """
    Exporta matriz a Excel
    
    Args:
        tipo: "sst" o "legal"
        matriz_id: ID de la matriz
    
    Returns:
        Archivo Excel (.xlsx)
    """
    try:
        mongodb = get_mongodb()
        
        # Obtener matriz de MongoDB
        if tipo == "sst":
            from models.matrices import MatrizSST
            matriz_data = mongodb.matrices_sst.find_one({"_id": matriz_id})
            if not matriz_data:
                raise HTTPException(status_code=404, detail="Matriz no encontrada")
            matriz = MatrizSST(**matriz_data)
            excel_data = excel_generator.generar_matriz_sst(matriz)
            filename = f"matriz_sst_{matriz.empresa}_{matriz_id[:8]}.xlsx"
            
        elif tipo == "legal":
            from models.matrices import MatrizLegal
            matriz_data = mongodb.matrices_legales.find_one({"_id": matriz_id})
            if not matriz_data:
                raise HTTPException(status_code=404, detail="Matriz no encontrada")
            matriz = MatrizLegal(**matriz_data)
            excel_data = excel_generator.generar_matriz_legal(matriz)
            filename = f"matriz_legal_{matriz.empresa}_{matriz_id[:8]}.xlsx"
            
        else:
            raise HTTPException(status_code=400, detail="tipo debe ser 'sst' o 'legal'")
        
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
async def list_matrices(tipo: Optional[str] = None):
    """
    Lista todas las matrices generadas
    
    Args:
        tipo: Filtrar por "sst" o "legal" (opcional)
    
    Returns:
        Lista de matrices
    """
    try:
        mongodb = get_mongodb()
        matrices = []
        
        if tipo is None or tipo == "sst":
            sst_matrices = mongodb.matrices_sst.find().sort("created_at", -1).limit(50)
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
        
        if tipo is None or tipo == "legal":
            legal_matrices = mongodb.matrices_legales.find().sort("created_at", -1).limit(50)
            for m in legal_matrices:
                matrices.append(MatrizResumen(
                    id=m["_id"],
                    tipo_matriz=TipoMatriz.LEGAL,
                    empresa=m["empresa"],
                    documento_origen=m["documento_origen"],
                    total_riesgos=m["total_riesgos"],
                    riesgos_criticos=m["riesgos_criticos"],
                    created_at=m["created_at"],
                    estado=m["estado"]
                ))
        
        # Ordenar por fecha
        matrices.sort(key=lambda x: x.created_at, reverse=True)
        
        return matrices
        
    except Exception as e:
        logger.error(f"Error listando matrices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
