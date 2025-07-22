"""
Servicio de autenticación y gestión de usuarios
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import os
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User, UserCreate, UserLogin, TokenResponse, TokenData, pwd_context
from ..models.database_models import Listing

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crear un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verificar y decodificar un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            email = payload.get("email")
            username = payload.get("username")
            
            if user_id is None or email is None:
                return None
                
            token_data = TokenData(user_id=user_id, email=email, username=username)
            return token_data
        except JWTError:
            return None
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email_or_username: str, password: str) -> Optional[User]:
        """Autenticar usuario con email/username y contraseña"""
        # Buscar por email o username
        stmt = select(User).where(
            or_(
                User.email == email_or_username,
                User.username == email_or_username
            )
        ).where(User.is_active.is_(True))
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
            
        if not pwd_context.verify(password, str(user.hashed_password)):
            return None
            
        # Actualizar último login
        await db.execute(
            User.__table__.update().where(User.id == user.id).values(last_login=datetime.utcnow())
        )
        await db.commit()
        
        return user
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Crear un nuevo usuario"""
        # Verificar que las contraseñas coincidan
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )
        
        # Verificar que el email no existe
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar que el username no existe
        stmt = select(User).where(User.username == user_data.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Crear el usuario
        hashed_password = pwd_context.hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_listings(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
        """Obtener los listings de un usuario"""
        stmt = select(Listing).where(
            Listing.user_id == user_id
        ).offset(skip).limit(limit).order_by(Listing.created_at.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()

# Dependencia para obtener el usuario actual
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependencia para obtener el usuario actual del token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = AuthService.verify_token(token)
    
    if token_data is None or token_data.user_id is None:
        raise credentials_exception
    
    user = await AuthService.get_user_by_id(db, token_data.user_id)
    
    if user is None:
        raise credentials_exception
    
    return user

# Dependencia opcional para el usuario (puede ser None)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Dependencia opcional para obtener el usuario actual"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        token_data = AuthService.verify_token(token)
        
        if token_data is None or token_data.user_id is None:
            return None
        
        user = await AuthService.get_user_by_id(db, token_data.user_id)
        return user
    except Exception:
        return None

# Dependencia para verificar admin
async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia para verificar que el usuario actual es admin"""
    if not bool(current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user
