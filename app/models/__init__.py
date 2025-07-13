from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ProductCategory(str, Enum):
    ELECTRONICS = "Electronics"
    HOME_GARDEN = "Home & Garden"
    CLOTHING = "Clothing, Shoes & Jewelry"
    SPORTS = "Sports & Outdoors"
    HEALTH = "Health & Personal Care"
    AUTOMOTIVE = "Automotive"
    TOYS = "Toys & Games"
    BOOKS = "Books"
    OTHER = "Other"

class ProductVariant(BaseModel):
    size: Optional[str] = None
    color: Optional[str] = None
    model: Optional[str] = None
    price_modifier: Optional[float] = 0.0

class CustomerProfile(BaseModel):
    age_range: str
    gender: Optional[str] = None
    interests: List[str]
    pain_points: List[str]
    use_cases: List[str]

class TechnicalSpecs(BaseModel):
    dimensions: Optional[str] = None
    weight: Optional[str] = None
    materials: List[str] = []
    compatibility: List[str] = []
    technical_requirements: List[str] = []

class BoxContents(BaseModel):
    main_product: str
    accessories: List[str] = []
    documentation: List[str] = []
    warranty_info: str
    certifications: List[str] = []

class PricingStrategy(BaseModel):
    initial_price: float
    competitor_price_range: Dict[str, float]  # {"min": 10.0, "max": 50.0}
    promotional_strategy: List[str]
    discount_structure: Dict[str, float]  # {"early_bird": 0.15, "bundle": 0.20}

class SEOKeywords(BaseModel):
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    search_terms: List[str]
    backend_keywords: List[str] = []

class VisualAssets(BaseModel):
    product_photos: List[str] = []  # URLs or file paths
    lifestyle_photos: List[str] = []
    infographics: List[str] = []
    renders: List[str] = []
    video_urls: List[str] = []

class ProductInput(BaseModel):
    # Pregunta 1: Producto y categorización
    product_name: str = Field(..., description="Nombre exacto del producto")
    category: ProductCategory = Field(..., description="Categoría de Amazon")
    variants: List[ProductVariant] = Field(default=[], description="Variantes del producto")
    
    # Pregunta 2: Cliente objetivo
    target_customer_description: str = Field(..., description="Descripción del cliente objetivo")
    use_situations: List[str] = Field(..., description="Situaciones de uso")
    
    # Pregunta 3: Propuesta de valor
    value_proposition: str = Field(..., description="Propuesta de valor diferencial")
    competitive_advantages: List[str] = Field(..., description="Ventajas competitivas")
    
    # Pregunta 4: Especificaciones
    raw_specifications: str = Field(..., description="Especificaciones técnicas en texto libre")
    
    # Pregunta 5: Contenido y garantías
    box_content_description: str = Field(..., description="Descripción del contenido de la caja")
    warranty_info: str = Field(..., description="Información de garantía")
    certifications: List[str] = Field(default=[], description="Certificaciones")
    
    # Pregunta 6: Estrategia de precios
    target_price: float = Field(..., description="Precio objetivo")
    pricing_strategy_notes: str = Field(..., description="Notas sobre estrategia de precios")
    
    # Pregunta 7: SEO y assets
    target_keywords: List[str] = Field(..., description="Palabras clave objetivo")
    available_assets: List[str] = Field(default=[], description="Assets visuales disponibles")
    asset_descriptions: List[str] = Field(default=[], description="Descripción de assets visuales")

class ProcessedListing(BaseModel):
    # Datos procesados por los agentes
    product_analysis: Dict[str, Any]
    customer_research: CustomerProfile
    value_proposition_analysis: Dict[str, Any]
    technical_specifications: TechnicalSpecs
    box_contents: BoxContents
    pricing_strategy: PricingStrategy
    seo_keywords: SEOKeywords
    visual_assets: VisualAssets
    
    # Listing final generado
    title: str
    bullet_points: List[str]
    description: str
    search_terms: List[str]
    backend_keywords: List[str]
    images_order: List[str]
    a_plus_content: Optional[str] = None
    
    # Metadatos
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_notes: List[str] = []
    recommendations: List[str] = []
    metadata: Optional[Dict[str, Any]] = {}
    database_id: Optional[int] = None  # ID de la base de datos si se guardó

class AgentResponse(BaseModel):
    agent_name: str
    status: str  # "success", "error", "partial"
    data: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time: float
    notes: List[str] = []
    recommendations: List[str] = []
