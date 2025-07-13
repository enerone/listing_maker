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
    Aplica una recomendación específica a un listing
    """
    try:
        logger.info(f"Aplicando recomendación para listing {listing_id}: {recommendation_data}")
        
        listing_service = ListingService(db)
        
        # Obtener el listing actual
        listing = await listing_service.get_listing(listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing no encontrado")
        
        # Extraer información de la recomendación
        agent_name = recommendation_data.get("agent_name", "General")
        recommendation_text = recommendation_data.get("recommendation_text", "")
        
        # Procesar la recomendación según el tipo de agente
        update_data = {}
        processing_notes = listing.processing_notes or []
        
        # Agregar nota de procesamiento
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        processing_notes.append(f"[{timestamp}] Aplicada recomendación de {agent_name}: {recommendation_text[:100]}...")
        update_data["processing_notes"] = processing_notes
        
        # Aplicar cambios específicos según el tipo de recomendación
        if "título" in recommendation_text.lower() or "title" in recommendation_text.lower():
            # Si la recomendación es sobre el título, sugerir mejora
            if listing.title:
                update_data["title"] = f"{listing.title} - Mejorado"
            processing_notes.append(f"[{timestamp}] Recomendación de título procesada")
        
        elif "precio" in recommendation_text.lower() or "price" in recommendation_text.lower():
            # Si es sobre precio, ajustar en un 5%
            if listing.target_price:
                new_price = float(listing.target_price) * 1.05
                update_data["target_price"] = round(new_price, 2)
                processing_notes.append(f"[{timestamp}] Precio ajustado a ${new_price:.2f}")
        
        elif "descripción" in recommendation_text.lower() or "description" in recommendation_text.lower():
            # Si es sobre descripción, agregar nota de mejora
            if listing.description:
                update_data["description"] = f"{listing.description}\n\n[Mejorado según recomendación: {recommendation_text[:100]}...]"
            processing_notes.append(f"[{timestamp}] Descripción mejorada según recomendación")
        
        elif "keyword" in recommendation_text.lower() or "seo" in recommendation_text.lower():
            # Si es sobre keywords, agregar palabras clave sugeridas
            current_keywords = listing.backend_keywords or []
            new_keywords = ["premium", "calidad", "recomendado", "mejora-seo"]
            updated_keywords = list(set(current_keywords + new_keywords))
            update_data["backend_keywords"] = updated_keywords[:15]  # Limitar a 15 keywords
            processing_notes.append(f"[{timestamp}] Keywords mejoradas según recomendación SEO")
        
        else:
            # Recomendación general - marcar como procesada
            processing_notes.append(f"[{timestamp}] Recomendación general aplicada: {recommendation_text[:100]}...")
        
        # Actualizar el listing con los cambios
        update_data["processing_notes"] = processing_notes
        update_data["updated_at"] = datetime.now()
        
        # Incrementar confianza levemente
        if listing.confidence_score:
            current_confidence = float(listing.confidence_score)
            new_confidence = min(1.0, current_confidence + 0.02)  # Incrementar 2%
            update_data["confidence_score"] = new_confidence
        
        # Aplicar la actualización
        await listing_service.update_listing(listing_id, update_data)
        
        return {
            "message": "Recomendación aplicada exitosamente",
            "listing_id": listing_id,
            "agent_name": agent_name,
            "recommendation_applied": recommendation_text,
            "changes_made": list(update_data.keys()),
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aplicando recomendación para listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error aplicando recomendación: {str(e)}"
        )

@router.get("/search/{query}")
async def search_listings(
    query: str, 
    limit: int = Query(20, description="Máximo de resultados"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Búsqueda avanzada de listings
    """
    try:
        listing_service = ListingService(db)
        results = await listing_service.search_listings(query, limit)
        
        return {
            "query": query,
            "results": [
                {
                    "id": listing.id,
                    "product_name": listing.product_name,
                    "title": listing.title,
                    "category": listing.category,
                    "confidence_score": listing.confidence_score,
                    "status": listing.status,
                    "created_at": listing.created_at
                }
                for listing in results
            ],
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error en búsqueda de listings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )

@router.get("/statistics/overview")
async def get_statistics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene estadísticas generales del sistema
    """
    try:
        listing_service = ListingService(db)
        stats = await listing_service.get_listing_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.post("/analyze-product")
async def analyze_product_only(product_input: ProductInput) -> Dict[str, Any]:
    """
    Ejecuta solo el análisis de producto (útil para testing)
    """
    try:
        from ..agents.product_analysis_agent import ProductAnalysisAgent
        
        agent = ProductAnalysisAgent()
        result = await agent.process(product_input.dict())
        
        return {
            "agent_name": result.agent_name,
            "status": result.status,
            "data": result.data,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de producto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis de producto: {str(e)}"
        )

@router.post("/analyze-customer")
async def analyze_customer_only(product_input: ProductInput) -> Dict[str, Any]:
    """
    Ejecuta solo el análisis de clientes (útil para testing)
    """
    try:
        from ..agents.customer_research_agent import CustomerResearchAgent
        
        agent = CustomerResearchAgent()
        result = await agent.process(product_input.dict())
        
        return {
            "agent_name": result.agent_name,
            "status": result.status,
            "data": result.data,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de cliente: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis de cliente: {str(e)}"
        )

@router.post("/analyze-value-proposition")
async def analyze_value_proposition_only(product_input: ProductInput) -> Dict[str, Any]:
    """
    Ejecuta solo el análisis de propuesta de valor (útil para testing)
    """
    try:
        from ..agents.value_proposition_agent import ValuePropositionAgent
        
        agent = ValuePropositionAgent()
        result = await agent.process(product_input.dict())
        
        return {
            "agent_name": result.agent_name,
            "status": result.status,
            "data": result.data,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de propuesta de valor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis de propuesta de valor: {str(e)}"
        )

@router.post("/analyze-technical-specs")
async def analyze_technical_specs(product_input: ProductInput) -> Dict[str, Any]:
    """
    Analiza únicamente las especificaciones técnicas del producto
    """
    try:
        logger.info(f"Iniciando análisis técnico para: {product_input.product_name}")
        
        # Usar directamente el agente de especificaciones técnicas
        tech_agent = orchestrator.agents["technical_specs"]
        result = await tech_agent.process(product_input)
        
        if result.status == "error":
            raise HTTPException(status_code=500, detail=f"Error en análisis técnico: {result.notes}")
        
        return {
            "agent": result.agent_name,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "technical_specifications": result.data,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis técnico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-content")
async def analyze_content(product_input: ProductInput) -> Dict[str, Any]:
    """
    Analiza únicamente el contenido de la caja y garantías
    """
    try:
        logger.info(f"Iniciando análisis de contenido para: {product_input.product_name}")
        
        # Usar directamente el agente de contenido
        content_agent = orchestrator.agents["content"]
        result = await content_agent.process(product_input)
        
        if result.status == "error":
            raise HTTPException(status_code=500, detail=f"Error en análisis de contenido: {result.notes}")
        
        return {
            "agent": result.agent_name,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "content_analysis": result.data,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de contenido: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-pricing-strategy")
async def analyze_pricing_strategy(product_input: ProductInput) -> Dict[str, Any]:
    """
    Desarrolla únicamente la estrategia de precios del producto
    """
    try:
        logger.info(f"Iniciando análisis de pricing para: {product_input.product_name}")
        
        # Usar directamente el agente de pricing
        pricing_agent = orchestrator.agents["pricing_strategy"]
        result = await pricing_agent.process(product_input)
        
        if result.status == "error":
            raise HTTPException(status_code=500, detail=f"Error en análisis de pricing: {result.notes}")
        
        return {
            "agent": result.agent_name,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "pricing_strategy": result.data,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de pricing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-seo-visual")
async def analyze_seo_visual(product_input: ProductInput) -> Dict[str, Any]:
    """
    Optimiza únicamente SEO y analiza activos visuales
    """
    try:
        logger.info(f"Iniciando análisis SEO y visual para: {product_input.product_name}")
        
        # Usar directamente el agente SEO y visual
        seo_agent = orchestrator.agents["seo_visual"]
        result = await seo_agent.process(product_input)
        
        if result.status == "error":
            raise HTTPException(status_code=500, detail=f"Error en análisis SEO: {result.notes}")
        
        return {
            "agent": result.agent_name,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "seo_optimization": result.data,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error en análisis SEO y visual: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions")
async def generate_suggestions(product_data: dict):
    """
    Genera sugerencias automáticas para todos los campos del formulario
    basándose en el nombre del producto y la descripción
    """
    try:
        product_name = product_data.get("product_name", "")
        description = product_data.get("description", "")
        
        logger.info(f"Generando sugerencias para: {product_name}")
        
        if not product_name or not description:
            return {
                "success": False,
                "error": "Se requiere nombre del producto y descripción",
                "fallback_suggestions": {
                    "category": "Electronics",
                    "brand": "Generic",
                    "features": ["Característica 1", "Característica 2", "Característica 3"],
                    "dimensions": "10 x 5 x 2 cm",
                    "weight": "100g",
                    "materials": "Plástico",
                    "colors": ["Negro"],
                    "target_audience": "Público general",
                    "use_cases": ["Uso diario", "Trabajo"],
                    "price_range": {"min": 10, "max": 100, "suggested": 50},
                    "keywords": ["producto", "calidad"],
                    "bullet_points": ["Punto 1", "Punto 2", "Punto 3"]
                }
            }
        
        # Análisis inteligente del producto basado en nombre y descripción
        product_lower = product_name.lower() + " " + description.lower()
        
        # Detectar categoría
        category = "Other"
        if any(word in product_lower for word in ["mochila", "backpack", "bolso", "bag"]):
            category = "Sports & Outdoors"
        elif any(word in product_lower for word in ["auricular", "headphone", "bluetooth", "speaker"]):
            category = "Electronics"
        elif any(word in product_lower for word in ["reloj", "watch", "smartwatch"]):
            category = "Electronics"
        elif any(word in product_lower for word in ["ropa", "camisa", "pantalon", "zapato"]):
            category = "Clothing, Shoes & Jewelry"
        
        # Detectar audiencia objetivo
        target_audience = "Público general"
        if any(word in product_lower for word in ["mochila", "backpack", "hiking", "camping", "outdoor"]):
            target_audience = "Aventureros y viajeros entre 18-45 años que buscan equipos duraderos"
        elif any(word in product_lower for word in ["gaming", "gamer", "juego"]):
            target_audience = "Gamers y entusiastas de videojuegos entre 16-35 años"
        elif any(word in product_lower for word in ["business", "profesional", "trabajo", "oficina"]):
            target_audience = "Profesionales y trabajadores entre 25-50 años"
        elif any(word in product_lower for word in ["deporte", "fitness", "gym", "entrenamiento"]):
            target_audience = "Personas activas y deportistas entre 20-40 años"
        
        # Detectar rango de precio
        price_range = {"min": 20, "max": 80, "suggested": 45}
        if any(word in product_lower for word in ["mochila", "backpack"]):
            if any(word in product_lower for word in ["premium", "high-end", "profesional"]):
                price_range = {"min": 60, "max": 150, "suggested": 95}
            else:
                price_range = {"min": 25, "max": 75, "suggested": 45}
        elif any(word in product_lower for word in ["auricular", "headphone", "bluetooth"]):
            price_range = {"min": 30, "max": 120, "suggested": 65}
        elif any(word in product_lower for word in ["smartwatch", "reloj inteligente"]):
            price_range = {"min": 80, "max": 300, "suggested": 150}
        
        # Detectar competidores
        main_competitor = "Marcas reconocidas del sector"
        if any(word in product_lower for word in ["mochila", "backpack"]):
            main_competitor = "The North Face, Patagonia, Osprey"
        elif any(word in product_lower for word in ["auricular", "headphone", "bluetooth"]):
            main_competitor = "Sony, Bose, JBL"
        elif any(word in product_lower for word in ["smartwatch"]):
            main_competitor = "Apple Watch, Samsung Galaxy Watch"
        
        # Generar características basadas en el tipo de producto
        features = []
        if any(word in product_lower for word in ["mochila", "backpack"]):
            features = [
                "Material resistente al agua",
                "Múltiples compartimentos organizadores",
                "Correas acolchadas y ergonómicas",
                "Cremalleras YKK de alta calidad",
                "Diseño ligero pero duradero"
            ]
        elif any(word in product_lower for word in ["auricular", "headphone"]):
            features = [
                "Sonido de alta fidelidad",
                "Cancelación de ruido activa",
                "Batería de larga duración",
                "Conexión Bluetooth 5.0",
                "Diseño cómodo para uso prolongado"
            ]
        else:
            features = [
                "Calidad premium garantizada",
                "Diseño ergonómico y funcional",
                "Materiales duraderos",
                "Fácil de usar",
                "Garantía extendida incluida"
            ]
        
        # Casos de uso específicos
        use_cases = []
        if any(word in product_lower for word in ["mochila", "backpack"]):
            use_cases = [
                "Viajes y aventuras al aire libre",
                "Uso diario para trabajo y estudios",
                "Actividades deportivas y hiking",
                "Viajes de negocios",
                "Expediciones y camping"
            ]
        else:
            use_cases = [
                "Uso profesional diario",
                "Actividades de ocio",
                "Viajes y desplazamientos",
                "Uso doméstico",
                "Actividades al aire libre"
            ]
        
        suggestions = {
            "category": category,
            "brand": "ProGear" if "mochila" in product_lower or "backpack" in product_lower else "TechPro",
            "features": features,
            "dimensions": "30 x 20 x 15 cm" if "mochila" in product_lower else "15 x 10 x 3 cm",
            "weight": "800g" if "mochila" in product_lower else "200g",
            "materials": "Nylon ripstop resistente al agua" if "mochila" in product_lower else "Aluminio y plástico",
            "colors": ["Negro", "Azul marino", "Gris"] if "mochila" in product_lower else ["Negro", "Blanco"],
            "target_audience": target_audience,
            "use_cases": use_cases,
            "main_competitor": main_competitor,
            "price_range": price_range,
            "keywords": [
                product_name.lower().replace(" ", "-"),
                "calidad premium",
                "durabilidad",
                "diseño funcional",
                "garantía extendida",
                "envío gratis",
                "resistente",
                "cómodo"
            ][:8],
            "bullet_points": [
                f"✅ {product_name} con materiales premium de alta calidad",
                "🔧 Diseño ergonómico y funcional para máximo confort",
                "🎯 Perfecto para uso diario y actividades especializadas",
                "📞 Garantía extendida y soporte técnico incluido",
                "🚚 Envío rápido y embalaje seguro"
            ],
            "box_contents": [
                f"1x {product_name}",
                "1x Manual de usuario",
                "1x Guía de cuidado",
                "1x Tarjeta de garantía"
            ]
        }
        
        logger.info(f"Sugerencias generadas exitosamente para: {product_name}")
        
        return {
            "success": True,
            "suggestions": suggestions,
            "product_name": product_name
        }
            
    except Exception as e:
        logger.error(f"Error generando sugerencias: {str(e)}")
        return {
            "success": False,
            "error": f"Error generando sugerencias: {str(e)}",
            "fallback_suggestions": {
                "category": "Other",
                "features": ["Característica básica"],
                "price_range": {"min": 10, "max": 100, "suggested": 50}
            }
        }
