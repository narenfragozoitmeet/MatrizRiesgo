"""
Sistema de autenticación y seguridad con JWT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de seguridad HTTP Bearer
security = HTTPBearer()


class AuthService:
    """Servicio de autenticación y manejo de JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica que la contraseña coincida con el hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera hash de contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT
        
        Args:
            data: Datos a incluir en el token (ej: {"sub": user_id})
            expires_delta: Tiempo de expiración personalizado
            
        Returns:
            Token JWT codificado
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.JWT_EXPIRATION_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Payload del token
            
        Raises:
            HTTPException: Si el token es inválido o expirado
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            
            return payload
            
        except JWTError as e:
            logger.error(f"Error verificando JWT: {str(e)}")
            raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency para obtener el usuario actual del token JWT
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        Payload del token con información del usuario
        
    Raises:
        HTTPException: Si el token es inválido
        
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            return {"user_id": current_user["sub"]}
    """
    token = credentials.credentials
    return AuthService.verify_token(token)


# Dependency opcional para rutas que pueden funcionar con o sin auth
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Dependency para obtener el usuario actual si está autenticado, None si no
    
    Usage:
        @app.get("/public-or-private")
        async def route(current_user: Optional[dict] = Depends(get_current_user_optional)):
            if current_user:
                # Usuario autenticado
                return {"message": "Hello " + current_user["sub"]}
            else:
                # Usuario anónimo
                return {"message": "Hello anonymous"}
    """
    if credentials is None:
        return None
    
    try:
        return AuthService.verify_token(credentials.credentials)
    except HTTPException:
        return None
