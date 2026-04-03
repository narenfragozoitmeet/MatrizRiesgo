from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import requests
import json
from io import BytesIO

from services.storage_service import init_storage, put_object, get_object
from services.document_parser import parse_document
from services.risk_analyzer import analyze_document_for_risks
from services.excel_generator import generate_risk_matrix_excel

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    original_filename: str
    storage_path: str
    content_type: str
    size: int
    uploaded_at: str

class RiskItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    categoria: str
    riesgo: str
    descripcion: str
    probabilidad: str
    impacto: str
    nivel_riesgo: str
    mitigacion: str

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    document_id: str
    document_name: str
    risks: List[RiskItem]
    summary: str
    total_risks: int
    created_at: str
    status: str

class AnalysisListItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    document_name: str
    total_risks: int
    created_at: str
    status: str

@api_router.get("/")
async def root():
    return {"message": "API de Matriz de Riesgos Legales"}

@api_router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document (PDF, Word, or Excel)"""
    try:
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado. Use PDF, Word o Excel.")
        
        ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        doc_id = str(uuid.uuid4())
        path = f"risk-matrix/uploads/{doc_id}.{ext}"
        data = await file.read()
        
        result = put_object(path, data, file.content_type or "application/octet-stream")
        
        doc_record = {
            "id": doc_id,
            "storage_path": result["path"],
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": result["size"],
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.documents.insert_one(doc_record)
        
        return DocumentUploadResponse(**doc_record)
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analyze/{document_id}", response_model=AnalysisResponse)
async def analyze_document(document_id: str):
    """Analyze uploaded document and generate risk matrix"""
    try:
        doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        data, content_type = get_object(doc["storage_path"])
        
        text_content = parse_document(data, doc["content_type"], doc["original_filename"])
        
        risks, summary = await analyze_document_for_risks(text_content, doc["original_filename"])
        
        analysis_id = str(uuid.uuid4())
        analysis_record = {
            "id": analysis_id,
            "document_id": document_id,
            "document_name": doc["original_filename"],
            "risks": [r.dict() for r in risks],
            "summary": summary,
            "total_risks": len(risks),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed"
        }
        
        await db.analyses.insert_one(analysis_record)
        
        return AnalysisResponse(**analysis_record)
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    risks = [RiskItem(**r) for r in analysis["risks"]]
    analysis["risks"] = risks
    return AnalysisResponse(**analysis)

@api_router.get("/download/{analysis_id}")
async def download_excel(analysis_id: str):
    """Download risk matrix as Excel file"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        
        risks = [RiskItem(**r) for r in analysis["risks"]]
        
        excel_data = generate_risk_matrix_excel(
            risks=risks,
            document_name=analysis["document_name"],
            summary=analysis["summary"]
        )
        
        filename = f"matriz_riesgos_{analysis['document_name'].rsplit('.', 1)[0]}.xlsx"
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error(f"Error generating Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyses", response_model=List[AnalysisListItem])
async def list_analyses():
    """List all analyses"""
    analyses = await db.analyses.find({}, {"_id": 0, "id": 1, "document_name": 1, "total_risks": 1, "created_at": 1, "status": 1}).sort("created_at", -1).to_list(100)
    return [AnalysisListItem(**a) for a in analyses]

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    try:
        init_storage()
        logger.info("Storage initialized successfully")
    except Exception as e:
        logger.error(f"Storage initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()