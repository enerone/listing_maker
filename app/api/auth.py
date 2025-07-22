"""
API endpoints para autenticación y gestión de usuarios
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..models.user import (
    User, UserCreate, UserLogin, UserResponse, UserUpdate, 
    ChangePassword, TokenResponse
)
from ..services.auth_service import (
    AuthService, get_current_user, get_current_admin_user
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

def user_to_response(user: User) -> UserResponse:
    """Convierte un objeto User de SQLAlchemy a UserResponse"""
    return UserResponse(
        id=int(user.id),
        email=str(user.email),
        username=str(user.username),
        full_name=str(user.full_name) if user.full_name else None,
        is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
        created_at=user.created_at,
        last_login=user.last_login
    )

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registrar un nuevo usuario"""
    try:
        # Crear el usuario
        user = await AuthService.create_user(db, user_data)
        
        # Generar token
        access_token = AuthService.create_access_token({
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        })
        
        # Convertir a UserResponse
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=bool(user.is_active),
            is_admin=bool(user.is_admin),
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return TokenResponse(
            access_token=access_token,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Iniciar sesión"""
    user = await AuthService.authenticate_user(
        db, 
        login_data.email_or_username, 
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar token
    access_token = AuthService.create_access_token({
        "user_id": user.id,
        "email": user.email,
        "username": user.username
    })
    
    # Convertir a UserResponse
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
        created_at=user.created_at,
        last_login=user.last_login
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obtener información del usuario actual"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=bool(current_user.is_active),
        is_admin=bool(current_user.is_admin),
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar información del usuario actual"""
    try:
        # Verificar email único si se va a cambiar
        if user_update.email and user_update.email != current_user.email:
            from sqlalchemy import select
            stmt = select(User).where(User.email == user_update.email, User.id != current_user.id)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está en uso"
                )
        
        # Verificar username único si se va a cambiar
        if user_update.username and user_update.username != current_user.username:
            from sqlalchemy import select
            stmt = select(User).where(User.username == user_update.username, User.id != current_user.id)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
        
        # Actualizar campos
        update_data = {}
        if user_update.email:
            update_data['email'] = user_update.email
        if user_update.username:
            update_data['username'] = user_update.username
        if user_update.full_name is not None:
            update_data['full_name'] = user_update.full_name
        
        if update_data:
            from sqlalchemy import update
            stmt = update(User).where(User.id == current_user.id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            await db.refresh(current_user)
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.full_name,
            is_active=bool(current_user.is_active),
            is_admin=bool(current_user.is_admin),
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando usuario: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    # Verificar contraseña actual
    from ..models.user import pwd_context
    if not pwd_context.verify(password_data.current_password, str(current_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Verificar que las nuevas contraseñas coincidan
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las nuevas contraseñas no coinciden"
        )
    
    # Actualizar contraseña
    new_hashed_password = pwd_context.hash(password_data.new_password)
    
    from sqlalchemy import update
    stmt = update(User).where(User.id == current_user.id).values(
        hashed_password=new_hashed_password
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}

@router.get("/my-listings")
async def get_my_listings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener los listings del usuario actual"""
    listings = await AuthService.get_user_listings(db, current_user.id, skip, limit)
    
    return {
        "listings": listings,
        "total": len(listings),
        "user_id": current_user.id
    }

# Endpoints de administración
@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener todos los usuarios (solo admin)"""
    from sqlalchemy import select
    stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=bool(user.is_active),
            is_admin=bool(user.is_admin),
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]

@router.post("/admin/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Activar/desactivar usuario (solo admin)"""
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    from sqlalchemy import update
    new_status = not bool(user.is_active)
    stmt = update(User).where(User.id == user_id).values(is_active=new_status)
    await db.execute(stmt)
    await db.commit()
    
    return {
        "message": f"Usuario {'activado' if new_status else 'desactivado'} exitosamente",
        "user_id": user_id,
        "is_active": new_status
    }
