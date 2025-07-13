from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base

class Listing(Base):
    """
    Modelo principal para almacenar listings completos
    """
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información básica del producto
    product_name = Column(String(500), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    target_price = Column(Float, nullable=False)
    
    # Datos de entrada originales (JSON)
    input_data = Column(JSON, nullable=False)
    
    # Listing generado
    title = Column(String(500), nullable=False)
    bullet_points = Column(JSON, nullable=False)  # Lista de strings
    description = Column(Text, nullable=False)
    search_terms = Column(JSON, nullable=False)  # Lista de strings
    backend_keywords = Column(JSON, nullable=False)  # Lista de strings
    images_order = Column(JSON, nullable=True)  # Lista de URLs/paths de imágenes
    a_plus_content = Column(Text, nullable=True)
    
    # Metadatos del procesamiento
    confidence_score = Column(Float, nullable=False, default=0.0)
    processing_notes = Column(JSON, nullable=True)  # Lista de strings
    recommendations = Column(JSON, nullable=True)  # Lista de strings
    
    # Status del listing
    status = Column(String(50), nullable=False, default="draft")  # draft, published, archived
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    agent_results = relationship("AgentResult", back_populates="listing", cascade="all, delete-orphan")
    listing_versions = relationship("ListingVersion", back_populates="listing", cascade="all, delete-orphan")

class AgentResult(Base):
    """
    Resultados individuales de cada agente
    """
    __tablename__ = "agent_results"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    
    # Información del agente
    agent_name = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # success, error, partial
    confidence = Column(Float, nullable=False, default=0.0)
    processing_time = Column(Float, nullable=False, default=0.0)
    
    # Datos del agente
    agent_data = Column(JSON, nullable=False)
    notes = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    listing = relationship("Listing", back_populates="agent_results")

class ListingVersion(Base):
    """
    Versiones históricas de listings para tracking de cambios
    """
    __tablename__ = "listing_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    
    version_number = Column(Integer, nullable=False)
    
    # Snapshot del listing en esta versión
    title = Column(String(500), nullable=False)
    bullet_points = Column(JSON, nullable=False)
    description = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Cambios realizados
    changes_made = Column(JSON, nullable=True)  # Lista de cambios
    change_reason = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    listing = relationship("Listing", back_populates="listing_versions")

class Project(Base):
    """
    Proyectos para agrupar múltiples listings relacionados
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuración del proyecto
    default_category = Column(String(100), nullable=True)
    target_market = Column(String(100), nullable=True)  # US, Argentina, etc.
    brand_name = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="active")  # active, archived
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ListingProject(Base):
    """
    Relación many-to-many entre listings y proyectos
    """
    __tablename__ = "listing_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Metadata de la relación
    role = Column(String(50), nullable=True)  # main_product, variant, bundle, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ListingMetrics(Base):
    """
    Métricas de performance de listings (para futuro)
    """
    __tablename__ = "listing_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    
    # Métricas de Amazon
    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    conversions = Column(Integer, nullable=True)
    revenue = Column(Float, nullable=True)
    
    # Métricas de ranking
    search_rank = Column(JSON, nullable=True)  # {"keyword": rank}
    bsr_rank = Column(Integer, nullable=True)  # Best Seller Rank
    
    # Fecha de las métricas
    metric_date = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
