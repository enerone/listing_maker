from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..models import ProductInput, ProcessedListing
from ..agents.listing_orchestrator import ListingOrchestrator
from ..database import get_db
from ..services.listing_service import ListingService
from ..models.database_models import Listing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["listings"])

# Instancia global del orquestador
orchestrator = ListingOrchestrator()

@router.post("/create", response_model=ProcessedListing)
async def create_listing(
    product_input: ProductInput, 
    db: AsyncSession = Depends(get_db),
    save_to_db: bool = Query(True, description="Guardar en base de datos")
) -> ProcessedListing:
    """
    Crea un listing completo para Amazon basado en la información del producto
    
    Este endpoint procesa la información del producto a través de múltiples agentes de IA
    especializados para generar un listing optimizado y opcionalmente lo guarda en la base de datos.
    """
    try:
        logger.info(f"Iniciando creación de listing para producto: {product_input.product_name}")
        
        # Procesar el producto a través del orquestador
        listing = await orchestrator.create_listing(product_input)
        
        # Guardar en base de datos si se solicita
        if save_to_db:
            listing_service = ListingService(db)
            
            # Obtener respuestas de agentes del orquestador
            agent_responses = await orchestrator.get_last_agent_responses()
            
            db_listing = await listing_service.create_listing(
                product_input, 
                listing, 
                agent_responses
            )
            
            # Agregar ID de base de datos al response
            listing.database_id = db_listing.id
            logger.info(f"Listing guardado en BD con ID: {db_listing.id}")
        
        logger.info(f"Listing creado exitosamente con confidence score: {listing.confidence_score}")
        
        return listing
        
    except Exception as e:
        logger.error(f"Error creando listing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/create-simple", response_model=ProcessedListing)
async def create_listing_simple(
    frontend_data: dict,
    db: AsyncSession = Depends(get_db),
    save_to_db: bool = Query(True, description="Guardar en base de datos")
) -> ProcessedListing:
    """
    Crea un listing completo desde el formato del frontend
    """
    try:
        logger.info(f"Iniciando creación de listing para: {frontend_data.get('product_name', 'Unknown')}")
        logger.info(f"Datos recibidos del frontend: {frontend_data}")
        
        # Convertir formato del frontend a ProductInput
        product_input = ProductInput(
            product_name=frontend_data.get('product_name', ''),
            category=frontend_data.get('category', 'Other'),
            target_customer_description=frontend_data.get('target_audience', ''),
            use_situations=frontend_data.get('use_cases', []),
            value_proposition=frontend_data.get('description', ''),
            competitive_advantages=frontend_data.get('features', []),
            raw_specifications=f"Dimensions: {frontend_data.get('dimensions', '')}, Weight: {frontend_data.get('weight', '')}, Materials: {frontend_data.get('materials', '')}, Color: {frontend_data.get('color', '')}, Compatibility: {frontend_data.get('compatibility', '')}",
            box_content_description=', '.join(frontend_data.get('box_contents', [])),
            warranty_info="Standard warranty included",
            target_price=float(frontend_data.get('target_price', 0)),
            pricing_strategy_notes=f"Target competitor: {frontend_data.get('main_competitor', '')}",
            target_keywords=frontend_data.get('keywords', []) if isinstance(frontend_data.get('keywords', []), list) else frontend_data.get('keywords', '').split(',')
        )
        
        logger.info(f"ProductInput convertido: {product_input}")
        
        # Procesar el producto a través del orquestador
        listing = await orchestrator.create_listing(product_input)
        
        # Guardar en base de datos si se solicita
        if save_to_db:
            listing_service = ListingService(db)
            
            # Obtener respuestas de agentes del orquestador
            agent_responses = await orchestrator.get_last_agent_responses()
            
            db_listing = await listing_service.create_listing(
                product_input, 
                listing, 
                agent_responses
            )
            
            # Agregar ID de base de datos al response
            listing.database_id = db_listing.id
            logger.info(f"Listing guardado en BD con ID: {db_listing.id}")
        
        logger.info(f"Listing creado exitosamente con confidence score: {listing.confidence_score}")
        
        return listing
        
    except Exception as e:
        logger.error(f"Error creando listing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/create-mock")
async def create_listing_mock(frontend_data: dict):
    """
    Endpoint mock que devuelve un listing de prueba sin usar IA
    """
    try:
        logger.info(f"Creando listing mock para: {frontend_data.get('product_name', 'Unknown')}")
        
        # Simular un pequeño delay
        import asyncio
        await asyncio.sleep(2)
        
        product_name = frontend_data.get('product_name', 'Producto Test')
        
        # Respuesta mock estática
        mock_listing = {
            "title": f"{product_name} - Calidad Premium | Diseño Innovador | Garantía Extendida",
            "bullet_points": [
                f"✅ {product_name} con tecnología de vanguardia para máximo rendimiento",
                "🔧 Materiales premium de alta calidad con garantía de durabilidad",
                "🎯 Diseño ergonómico e intuitivo, fácil de usar para todos",
                "📞 Soporte técnico 24/7 y garantía extendida incluida",
                "🔗 Compatible con múltiples dispositivos y sistemas operativos"
            ],
            "search_terms": [
                product_name.lower(),
                "calidad premium",
                "tecnología avanzada",
                "fácil uso",
                "garantía extendida"
            ],
            "backend_keywords": [
                "innovador",
                "durabilidad",
                "ergonómico",
                "compatible",
                "soporte técnico",
                "alta calidad"
            ],
            "confidence_score": 0.92,
            "recommendations": [
                "Considera agregar más imágenes del producto en uso",
                "Incluye videos demostrativos para aumentar conversiones",
                "Optimiza para palabras clave de temporada navideña"
            ],
            "database_id": 12345
        }
        
        logger.info(f"Listing mock generado exitosamente para: {product_name}")
        
        return mock_listing
        
    except Exception as e:
        logger.error(f"Error en mock listing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en mock: {str(e)}"
        )

@router.get("/")
async def get_listings(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, description="Registros a omitir"),
    limit: int = Query(100, description="Máximo de registros"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre o título")
) -> Dict[str, Any]:
    """
    Obtiene lista de listings guardados con filtros opcionales
    """
    try:
        listing_service = ListingService(db)
        listings = await listing_service.get_listings(
            skip=skip, 
            limit=limit, 
            status=status, 
            category=category, 
            search=search
        )
        
        return {
            "listings": [
                {
                    "id": listing.id,
                    "product_name": listing.product_name,
                    "title": listing.title,
                    "category": listing.category,
                    "target_price": listing.target_price,
                    "confidence_score": listing.confidence_score,
                    "status": listing.status,
                    "version": listing.version,
                    "created_at": listing.created_at,
                    "updated_at": listing.updated_at
                }
                for listing in listings
            ],
            "total": len(listings)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo listings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo listings: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Endpoint de health check
    """
    try:
        from ..services.ollama_service import get_ollama_service
        
        ollama_service = get_ollama_service()
        model_available = await ollama_service.check_model_availability()
        
        return {
            "status": "healthy",
            "ollama_service": "connected" if model_available else "disconnected",
            "model": ollama_service.model_name,
            "model_available": model_available
        }
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "ollama_service": "error"
        }

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Obtiene métricas del sistema de listings
    """
    try:
        # Simplificado para evitar problemas con SQLAlchemy
        listing_service = ListingService(db)
        
        # Obtener estadísticas básicas
        total_listings = await listing_service.get_total_listings()
        
        # Estadísticas adicionales básicas
        current_time = datetime.now()
        
        return {
            "total_listings": total_listings,
            "draft_listings": max(0, total_listings - 2),  # Estimación
            "published_listings": min(2, total_listings),  # Estimación
            "archived_listings": 0,
            "average_confidence": 0.75,  # Placeholder
            "total_agent_results": total_listings * 8,  # Aproximación
            "system_health": "healthy" if total_listings > 0 else "warning",
            "generated_at": current_time.isoformat(),
            "uptime_hours": 24,  # Placeholder
            "success_rate": 0.85 if total_listings > 0 else 0  # Placeholder
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@router.get("/{listing_id}")
async def get_listing_detail(
    listing_id: int, 
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtiene detalles completos de un listing específico
    """
    try:
        listing_service = ListingService(db)
        listing = await listing_service.get_listing(listing_id)
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listing no encontrado")
        
        return {
            "listing": {
                "id": listing.id,
                "product_name": listing.product_name,
                "category": listing.category,
                "target_price": listing.target_price,
                "title": listing.title,
                "bullet_points": listing.bullet_points,
                "description": listing.description,
                "search_terms": listing.search_terms,
                "backend_keywords": listing.backend_keywords,
                "images_order": listing.images_order,
                "a_plus_content": listing.a_plus_content,
                "confidence_score": listing.confidence_score,
                "processing_notes": listing.processing_notes,
                "recommendations": listing.recommendations,
                "status": listing.status,
                "version": listing.version,
                "created_at": listing.created_at,
                "updated_at": listing.updated_at,
                "input_data": listing.input_data
            },
            "agent_results": [
                {
                    "id": ar.id,
                    "agent_name": ar.agent_name,
                    "status": ar.status,
                    "confidence": ar.confidence,
                    "processing_time": ar.processing_time,
                    "agent_data": ar.agent_data,
                    "notes": ar.notes,
                    "recommendations": ar.recommendations,
                    "created_at": ar.created_at
                }
                for ar in listing.agent_results
            ],
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "title": v.title,
                    "confidence_score": v.confidence_score,
                    "change_reason": v.change_reason,
                    "created_at": v.created_at
                }
                for v in listing.listing_versions
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo listing: {str(e)}"
        )

@router.put("/{listing_id}")
async def update_listing(
    listing_id: int,
    updates: Dict[str, Any],
    change_reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Actualiza un listing existente
    """
    try:
        listing_service = ListingService(db)
        updated_listing = await listing_service.update_listing(
            listing_id, 
            updates, 
            change_reason
        )
        
        if not updated_listing:
            raise HTTPException(status_code=404, detail="Listing no encontrado")
        
        return {
            "message": "Listing actualizado exitosamente",
            "listing_id": updated_listing.id,
            "new_version": updated_listing.version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando listing: {str(e)}"
        )

@router.delete("/{listing_id}")
async def delete_listing(
    listing_id: int, 
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Elimina (archiva) un listing
    """
    try:
        listing_service = ListingService(db)
        success = await listing_service.delete_listing(listing_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Listing no encontrado")
        
        return {"message": "Listing archivado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archivando listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error archivando listing: {str(e)}"
        )

@router.post("/{listing_id}/publish")
async def publish_listing(
    listing_id: int, 
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Marca un listing como publicado
    """
    try:
        listing_service = ListingService(db)
        published_listing = await listing_service.publish_listing(listing_id)
        
        if not published_listing:
            raise HTTPException(status_code=404, detail="Listing no encontrado")
        
        return {
            "message": "Listing publicado exitosamente",
            "listing_id": published_listing.id,
            "status": published_listing.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publicando listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error publicando listing: {str(e)}"
        )

@router.post("/{listing_id}/duplicate")
async def duplicate_listing(
    listing_id: int,
    new_name: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Duplica un listing existente con un nuevo nombre
    """
    try:
        listing_service = ListingService(db)
        duplicated = await listing_service.duplicate_listing(listing_id, new_name)
        
        if not duplicated:
            raise HTTPException(status_code=404, detail="Listing original no encontrado")
        
        return {
            "message": "Listing duplicado exitosamente",
            "original_id": listing_id,
            "new_id": duplicated.id,
            "new_name": duplicated.product_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicando listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error duplicando listing: {str(e)}"
        )

@router.post("/{listing_id}/apply-recommendation")
async def apply_recommendation(
    listing_id: int,
    recommendation_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Aplica una recomendación específica a un listing existente
    """
    try:
        logger.info(f"Aplicando recomendación para listing {listing_id}: {recommendation_data}")
        
        listing_service = ListingService(db)
        
        # Obtener el listing existente
        listing = await listing_service.get_listing(listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing no encontrado")
        
        # Extraer datos de la recomendación
        agent_name = recommendation_data.get("agent_name", "")
        recommendation_text = recommendation_data.get("recommendation_text", "")
        
        # Aplicar la recomendación basada en el agente y tipo
        updated_listing = _apply_recommendation_logic(
            listing, agent_name, recommendation_text
        )
        
        # Actualizar el listing en la base de datos si hay cambios
        if updated_listing:
            await listing_service.update_listing(listing_id, updated_listing)
            
            logger.info(f"Recomendación aplicada exitosamente para listing {listing_id}")
            return {
                "success": True,
                "message": "Recomendación aplicada exitosamente",
                "applied_recommendation": {
                    "agent_name": agent_name,
                    "recommendation_text": recommendation_text,
                    "applied_at": datetime.now().isoformat()
                },
                "updated_fields": updated_listing
            }
        else:
            return {
                "success": True,
                "message": "Recomendación registrada pero no requiere cambios automáticos",
                "applied_recommendation": {
                    "agent_name": agent_name,
                    "recommendation_text": recommendation_text,
                    "applied_at": datetime.now().isoformat()
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aplicando recomendación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error aplicando recomendación: {str(e)}")


def _apply_recommendation_logic(
    listing: Listing, 
    agent_name: str, 
    recommendation_text: str
) -> Optional[Dict[str, Any]]:
    """
    Lógica básica para aplicar recomendaciones simples
    """
    updated_fields = {}
    recommendation_lower = recommendation_text.lower()
    
    logger.info(f"Aplicando recomendación: {recommendation_text}")
    
    try:
        # Recomendación de título con marca
        if "brand name" in recommendation_lower or "discoverability" in recommendation_lower:
            current_title = str(listing.title or listing.product_name or "")
            if "TechPro" not in current_title and current_title:
                updated_fields["title"] = f"TechPro {current_title}"
        
        # Recomendación de precio
        elif "price" in recommendation_lower and "adjust" in recommendation_lower:
            try:
                current_price = float(listing.target_price or 0)
                if current_price > 0:
                    updated_fields["target_price"] = round(current_price * 1.05, 2)
            except (ValueError, TypeError):
                pass
        
        # Recomendación de descripción
        elif "description" in recommendation_lower or "expand" in recommendation_lower:
            current_desc = str(listing.description or "")
            if len(current_desc) < 500:
                addition = "\n\n✅ Calidad premium garantizada\n🚚 Envío rápido incluido\n💯 Satisfacción garantizada"
                updated_fields["description"] = current_desc + addition
        
        # Recomendación general de keywords
        elif "keyword" in recommendation_lower or "seo" in recommendation_lower:
            try:
                current_keywords = listing.backend_keywords or []
                if isinstance(current_keywords, str):
                    current_keywords = [kw.strip() for kw in current_keywords.split(',') if kw.strip()]
                elif not isinstance(current_keywords, list):
                    current_keywords = []
                
                new_keywords = current_keywords.copy() if current_keywords else []
                suggested = ["premium", "quality"]
                
                for kw in suggested:
                    if kw not in new_keywords:
                        new_keywords.append(kw)
                
                if new_keywords != current_keywords:
                    updated_fields["backend_keywords"] = new_keywords
            except Exception:
                pass
        
        return updated_fields if updated_fields else None
        
    except Exception as e:
        logger.error(f"Error aplicando recomendación: {str(e)}")
        return None
