"""
API de autenticación - Login, registro, etc.
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from db.mongodb import mongodb
from core.security import AuthService, get_current_user
from models.user import UserCreate, UserResponse, Token
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    """Request de login"""
    email: EmailStr
    password: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, user_data: UserCreate):
    """
    Registrar nuevo usuario
    
    - Verifica que el email no exista
    - Hashea la contraseña
    - Crea el usuario en MongoDB
    """
    db = mongodb.db
    
    # Verificar si el usuario ya existe
    existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    user = {
        "id": str(uuid4()),
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": AuthService.get_password_hash(user_data.password),
        "is_active": True,
        "is_admin": False,  # Primer usuario podría ser admin
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Si es el primer usuario, hacerlo admin
    user_count = await db.users.count_documents({})
    if user_count == 0:
        user["is_admin"] = True
        logger.info("Primer usuario creado como administrador")
    
    await db.users.insert_one(user)
    
    # Retornar sin el hash de password
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        is_admin=user["is_admin"],
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )


@router.post("/login", response_model=Token)
async def login(request: Request, login_data: LoginRequest):
    """
    Login de usuario
    
    - Verifica credenciales
    - Genera token JWT
    """
    db = mongodb.db
    
    # Buscar usuario
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar contraseña
    if not AuthService.verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar que el usuario esté activo
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token JWT
    access_token = AuthService.create_access_token(
        data={
            "sub": user["id"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False)
        }
    )
    
    logger.info(f"Usuario {user['email']} ha iniciado sesión")
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Obtener información del usuario actual
    
    Requiere autenticación JWT
    """
    db = mongodb.db
    
    user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        is_admin=user.get("is_admin", False),
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )


@router.post("/logout")
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Logout (placeholder - en JWT el logout se maneja en el cliente eliminando el token)
    
    En una implementación más avanzada, aquí podrías:
    - Agregar el token a una blacklist en Redis
    - Invalidar refresh tokens
    """
    logger.info(f"Usuario {current_user['email']} ha cerrado sesión")
    return {"message": "Sesión cerrada exitosamente"}
