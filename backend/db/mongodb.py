"""MongoDB Connection & Collections Manager"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MongoDB:
    """Singleton MongoDB manager"""
    _instance: Optional['MongoDB'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Establece conexión con MongoDB"""
        try:
            self._client = MongoClient(
                settings.MONGO_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[settings.DB_NAME]
            logger.info(f"✅ MongoDB conectado: {settings.DB_NAME}")
            self._create_indexes()
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Crea índices para mejor performance"""
        try:
            # Índices para documentos_bronze
            self.documentos_bronze.create_index("filename")
            self.documentos_bronze.create_index("empresa")
            self.documentos_bronze.create_index("created_at")
            
            # Índices para matrices
            self.matrices_sst.create_index("empresa")
            self.matrices_sst.create_index("document_id")
            self.matrices_sst.create_index("created_at")
            
            self.matrices_legales.create_index("empresa")
            self.matrices_legales.create_index("document_id")
            self.matrices_legales.create_index("created_at")
            
            logger.info("✅ Índices MongoDB creados")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron crear índices: {str(e)}")
    
    @property
    def db(self) -> Database:
        """Retorna la base de datos"""
        if self._db is None:
            self.connect()
        return self._db
    
    # === COLECCIONES ===
    
    @property
    def documentos_bronze(self) -> Collection:
        """Capa Bronze: Documentos originales sin procesar"""
        return self.db["documentos_bronze"]
    
    @property
    def analisis_silver(self) -> Collection:
        """Capa Silver: Datos procesados y limpios"""
        return self.db["analisis_silver"]
    
    @property
    def matrices_sst(self) -> Collection:
        """Capa Gold: Matrices GTC 45 (SST)"""
        return self.db["matrices_sst"]
    
    @property
    def matrices_legales(self) -> Collection:
        """Capa Gold: Matrices Riesgos Legales"""
        return self.db["matrices_legales"]
    
    def close(self):
        """Cierra la conexión"""
        if self._client:
            self._client.close()
            logger.info("MongoDB desconectado")

# Singleton instance
mongodb = MongoDB()

def get_mongodb() -> MongoDB:
    """Dependency injection para FastAPI"""
    return mongodb
