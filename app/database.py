import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./listings.db")

# Configuración del motor de base de datos
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries en desarrollo
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Sesión de base de datos
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

async def get_db():
    """
    Dependency para obtener sesión de base de datos
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """
    Crear todas las tablas
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """
    Eliminar todas las tablas (útil para desarrollo)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
