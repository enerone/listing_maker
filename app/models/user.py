"""
Modelos de usuario y autenticación
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

from ..database import Base

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """Modelo de usuario en la base de datos"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Preferencias del usuario
    preferences = Column(Text, nullable=True)  # JSON string con preferencias
    
    # Relaciones
    listings = relationship("Listing", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return pwd_context.verify(password, str(self.hashed_password))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash de la contraseña"""
        return pwd_context.hash(password)
    
    def generate_token(self) -> str:
        """Genera un JWT token para el usuario"""
        secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
        payload = {
            "user_id": self.id,
            "email": self.email,
            "username": self.username,
            "exp": datetime.utcnow() + timedelta(days=7)  # Token válido por 7 días
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")

# === PYDANTIC MODELS ===

class UserBase(BaseModel):
    """Base del modelo de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "username": "miusuario",
                "full_name": "Mi Nombre Completo",
                "password": "mipassword123",
                "confirm_password": "mipassword123"
            }
        }

class UserLogin(BaseModel):
    """Modelo para login"""
    email_or_username: str = Field(..., description="Email o nombre de usuario")
    password: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_or_username": "usuario@ejemplo.com",
                "password": "mipassword123"
            }
        }

class UserResponse(UserBase):
    """Modelo de respuesta de usuario"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)

class ChangePassword(BaseModel):
    """Modelo para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)

class TokenResponse(BaseModel):
    """Respuesta con token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 604800  # 7 días en segundos

class TokenData(BaseModel):
    """Datos del token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
