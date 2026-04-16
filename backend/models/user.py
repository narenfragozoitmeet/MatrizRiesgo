"""
Modelo de Usuario para autenticación
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Esquema base de usuario"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=8, description="Contraseña mínimo 8 caracteres")


class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Esquema de usuario en base de datos"""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    """Esquema de respuesta de usuario (sin password)"""
    id: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Esquema de token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos del token decodificado"""
    user_id: Optional[str] = None
