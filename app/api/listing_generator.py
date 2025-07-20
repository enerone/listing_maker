"""
API endpoints para el generador de listings de Amazon
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.seo_visual_agent import SEOVisualAgent
from ..agents.amazon_copywriter_agent import AmazonCopywriterAgent
from ..models import ProductInput, ProductCategory
from ..database import get_db
from ..services.image_generation_service import get_image_generation_service

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Pydantic models para las requests
class KeywordGenerationRequest(BaseModel):
    title: str
    description: str
    category: str
    brand: str
    manual_keywords: Optional[List[str]] = []

class ListingGenerationRequest(BaseModel):
    title: str
    description: str
    category: str
    brand: str
    keywords: List[str]

class SuggestionApplication(BaseModel):
    suggestion_id: str
    session_id: str  # Añadir session_id explícito
    field: str  # 'title', 'bullets', 'description'
    content: str
    edited_content: Optional[str] = None

class SuggestionRegeneration(BaseModel):
    suggestion_id: str
    session_id: str
    field: str
    current_content: str
    regeneration_type: str  # 'improve', 'alternative', 'shorter', 'longer'

class SaveListingRequest(BaseModel):
    session_id: str
    save_as_draft: bool = True

# Estado temporal para tracking de cambios
listing_sessions = {}

@router.get("/generator", response_class=HTMLResponse)
async def listing_generator_page(request: Request):
    """Página principal del generador de listings"""
    return templates.TemplateResponse("listing_generator.html", {
        "request": request,
        "title": "Generador de Listings Amazon"
    })

@router.post("/api/generate-keywords")
async def generate_keywords(request: KeywordGenerationRequest):
    """Genera keywords usando el SEO Visual Agent"""
    try:
        logger.info(f"🔍 Generando keywords para: {request.title}")
        
        # Crear input para el agente SEO
        product_input = ProductInput(
            product_name=request.title,
            value_proposition=request.description,
            category=ProductCategory.ELECTRONICS,  # Default, se puede mapear
            target_keywords=request.manual_keywords or [],
            competitive_advantages=[],
            use_situations=[],
            target_price=0.0,
            target_customer_description="",
            pricing_strategy_notes="",
            raw_specifications="",
            box_content_description="",
            warranty_info="",
            certifications=[]
        )
        
        # Instanciar y ejecutar agente SEO
        seo_agent = SEOVisualAgent()
        logger.info("Ejecutando agente SEO...")
        seo_result = await seo_agent.process(product_input)
        
        logger.info(f"Resultado SEO - Status: {seo_result.status}, Confidence: {seo_result.confidence}")
        logger.info(f"Datos SEO: {seo_result.data}")
        
        if seo_result.status == "success":
            # Extraer keywords del resultado
            seo_data = seo_result.data
            primary_keywords = seo_data.get("seo_strategy", {}).get("primary_keywords", [])
            secondary_keywords = seo_data.get("seo_strategy", {}).get("secondary_keywords", [])
            long_tail_keywords = seo_data.get("seo_strategy", {}).get("long_tail_keywords", [])
            
            all_keywords = primary_keywords + secondary_keywords + long_tail_keywords
            
            # Combinar con keywords manuales
            if request.manual_keywords:
                all_keywords = list(set(all_keywords + request.manual_keywords))
            
            return {
                "success": True,
                "keywords": all_keywords[:20],  # Limitar a 20 keywords
                "primary_keywords": primary_keywords,
                "secondary_keywords": secondary_keywords,
                "long_tail_keywords": long_tail_keywords,
                "confidence": seo_result.confidence,
                "agent": "seo_visual_agent"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Error en SEO agent: {seo_result.notes}")
            
    except Exception as e:
        logger.error(f"❌ Error generando keywords: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "keywords": request.manual_keywords or []
        }

@router.post("/api/generate-listing")
async def generate_listing(request: ListingGenerationRequest, db: AsyncSession = Depends(get_db)):
    """Genera el listing completo usando Amazon Copywriter Agent y lo guarda en la base de datos"""
    try:
        logger.info(f"🖋️ Generando listing para: {request.title}")
        
        # Crear input para el agente de copywriter
        product_data = {
            "product_name": request.title,
            "value_proposition": request.description,
            "category": request.category,
            "brand": request.brand,
            "target_keywords": request.keywords,
            "competitive_advantages": [],
            "use_situations": [],
            "raw_specifications": "",
            "target_customer_description": "",
            "customer_analysis": {},
            "competitive_analysis": {},
            "seo_keywords": request.keywords
        }
        
        # Instanciar y ejecutar agente de copywriter
        copywriter_agent = AmazonCopywriterAgent()
        copywriter_result = await copywriter_agent.process(product_data)
        
        logger.info(f"Resultado Copywriter - Status: {copywriter_result.status}, Confidence: {copywriter_result.confidence}")
        logger.info(f"Datos Copywriter: {copywriter_result.data}")
        
        if copywriter_result.status == "success":
            copywriter_data = copywriter_result.data
            
            # Generar ID de sesión para tracking de cambios
            session_id = f"session_{len(listing_sessions) + 1}"
            
            # Guardar estado inicial
            listing_sessions[session_id] = {
                "original": copywriter_data.copy(),
                "current": copywriter_data.copy(),
                "suggestions": [],
                "applied_suggestions": [],
                "product_data": product_data,
                "database_id": None  # Se llenará después del guardado
            }
            
            # GUARDAR AUTOMÁTICAMENTE EN LA BASE DE DATOS
            try:
                # Crear ProcessedListing directamente con los datos del agente
                from ..models import ProcessedListing, CustomerProfile, TechnicalSpecs, BoxContents, PricingStrategy, SEOKeywords, VisualAssets, AgentResponse
                
                # Crear estructuras de datos necesarias según las definiciones exactas
                customer_profile = CustomerProfile(
                    age_range="25-45",
                    gender=None,
                    interests=["Technology", "Quality products"],
                    pain_points=["Need for reliable products"],
                    use_cases=copywriter_data.get("use_situations", ["General use"])
                )
                
                technical_specs = TechnicalSpecs(
                    dimensions=copywriter_data.get("dimensions"),
                    weight=copywriter_data.get("weight"),
                    materials=copywriter_data.get("materials", "").split(",") if copywriter_data.get("materials") else [],
                    compatibility=copywriter_data.get("compatibility", "").split(",") if copywriter_data.get("compatibility") else [],
                    technical_requirements=[]
                )
                
                box_contents = BoxContents(
                    main_product=request.title,
                    accessories=copywriter_data.get("box_content", []) if isinstance(copywriter_data.get("box_content"), list) else [],
                    documentation=["User manual", "Warranty card"],
                    warranty_info="Standard warranty included",
                    certifications=[]
                )
                
                pricing_strategy = PricingStrategy(
                    initial_price=0.0,
                    competitor_price_range={"min": 0.0, "max": 100.0},
                    promotional_strategy=["Standard promotions"],
                    discount_structure={"standard": 0.10}
                )
                
                seo_keywords = SEOKeywords(
                    primary_keywords=request.keywords[:3] if len(request.keywords) >= 3 else request.keywords,
                    secondary_keywords=request.keywords[3:] if len(request.keywords) > 3 else [],
                    long_tail_keywords=copywriter_data.get("search_terms", []) if isinstance(copywriter_data.get("search_terms"), list) else [],
                    search_terms=copywriter_data.get("search_terms", request.keywords) if isinstance(copywriter_data.get("search_terms"), list) else request.keywords,
                    backend_keywords=copywriter_data.get("backend_keywords", "").split(", ") if isinstance(copywriter_data.get("backend_keywords"), str) else (copywriter_data.get("backend_keywords", []) if isinstance(copywriter_data.get("backend_keywords"), list) else [])
                )
                
                visual_assets = VisualAssets(
                    product_photos=[],
                    lifestyle_photos=[],
                    infographics=[],
                    renders=[],
                    video_urls=[]
                )
                
                # Crear el ProcessedListing completo
                processed_listing = ProcessedListing(
                    product_analysis={
                        "category": request.category,
                        "brand": request.brand,
                        "main_features": copywriter_data.get("bullet_points", []) if isinstance(copywriter_data.get("bullet_points"), list) else [],
                        "competitive_advantages": copywriter_data.get("competitive_advantages", [])
                    },
                    customer_research=customer_profile,
                    value_proposition_analysis={
                        "core_benefits": copywriter_data.get("value_proposition", ""),
                        "unique_selling_points": (copywriter_data.get("bullet_points", []) if isinstance(copywriter_data.get("bullet_points"), list) else [])[:3]
                    },
                    technical_specifications=technical_specs,
                    box_contents=box_contents,
                    pricing_strategy=pricing_strategy,
                    seo_keywords=seo_keywords,
                    visual_assets=visual_assets,
                    title=copywriter_data.get("main_title", request.title),
                    bullet_points=copywriter_data.get("bullet_points", []) if isinstance(copywriter_data.get("bullet_points"), list) else [],
                    description=copywriter_data.get("product_description", request.description),
                    search_terms=copywriter_data.get("search_terms", request.keywords) if isinstance(copywriter_data.get("search_terms"), list) else request.keywords,
                    backend_keywords=copywriter_data.get("backend_keywords", "").split(", ") if isinstance(copywriter_data.get("backend_keywords"), str) else (copywriter_data.get("backend_keywords", []) if isinstance(copywriter_data.get("backend_keywords"), list) else []),
                    images_order=[],
                    image_ai_prompts=copywriter_data.get("image_ai_prompts", {}),
                    a_plus_content=json.dumps(copywriter_data.get("a_plus_content")) if isinstance(copywriter_data.get("a_plus_content"), dict) else copywriter_data.get("a_plus_content"),
                    confidence_score=copywriter_result.confidence,
                    processing_notes=[f"Generated by Amazon Copywriter Agent - Confidence: {copywriter_result.confidence}"],
                    recommendations=copywriter_result.notes if hasattr(copywriter_result, 'notes') and isinstance(copywriter_result.notes, list) else [],
                    metadata={
                        "generation_timestamp": datetime.now().isoformat(),
                        "agent_used": "amazon_copywriter_agent",
                        "original_input": product_data,
                        "agent_data": copywriter_data
                    }
                )
                
                # Guardar usando el servicio de listing
                from ..services.listing_service import ListingService
                listing_service = ListingService(db)
                
                # Crear ProductInput para el servicio
                product_input = ProductInput(
                    product_name=request.title,
                    category=ProductCategory.ELECTRONICS,  # Mapear categoría apropiadamente
                    value_proposition=request.description,
                    target_keywords=request.keywords,
                    competitive_advantages=[],
                    use_situations=[],
                    target_price=0.0,
                    target_customer_description="",
                    pricing_strategy_notes="",
                    raw_specifications="",
                    box_content_description="",
                    warranty_info="",
                    certifications=[]
                )
                
                # Crear respuesta de agente correctamente tipada
                agent_response_obj = AgentResponse(
                    agent_name="amazon_copywriter_agent",
                    status=copywriter_result.status,
                    data=copywriter_data,
                    confidence=copywriter_result.confidence,
                    processing_time=0.0,
                    notes=copywriter_result.notes if hasattr(copywriter_result, 'notes') and isinstance(copywriter_result.notes, list) else []
                )
                
                agent_responses = {
                    "amazon_copywriter_agent": agent_response_obj
                }
                
                db_listing = await listing_service.create_listing(
                    product_input, 
                    processed_listing, 
                    agent_responses
                )
                
                # Actualizar sesión con ID de base de datos
                listing_sessions[session_id]["database_id"] = db_listing.id
                processed_listing.database_id = db_listing.id
                logger.info(f"✅ Listing completo guardado en base de datos con ID: {db_listing.id}")
                
            except Exception as db_error:
                logger.error(f"❌ Error guardando en base de datos: {str(db_error)}")
                logger.error(f"Detalles del error: {db_error.__class__.__name__}: {str(db_error)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continuar sin fallar si hay error en DB
            
            # Generar sugerencias automáticas
            suggestions = await _generate_suggestions(copywriter_data, product_data)
            listing_sessions[session_id]["suggestions"] = suggestions
            
            # Generar imágenes del producto usando Stable Diffusion
            generated_images = []
            try:
                logger.info(f"🎨 Iniciando generación de imágenes para: {request.title}")
                image_service = get_image_generation_service()
                
                # Debug: verificar contenido del copywriter_data
                logger.info(f"🔍 Debug copywriter_data keys: {list(copywriter_data.keys())}")
                
                # Verificar si el copywriter generó prompts IA específicos
                ai_prompts = copywriter_data.get("image_ai_prompts", {})
                logger.info(f"🔍 Debug ai_prompts encontrados: {ai_prompts}")
                
                if ai_prompts and len(ai_prompts) > 0:
                    logger.info(f"🎨 Usando prompts IA específicos del copywriter: {list(ai_prompts.keys())}")
                    images = await image_service.generate_images_from_ai_prompts(
                        product_name=request.title,
                        ai_prompts=ai_prompts,
                        session_id=session_id
                    )
                else:
                    logger.info("🎨 Usando generación estándar de imágenes")
                    images = await image_service.generate_product_images(
                        product_name=request.title,
                        description=request.description,
                        num_images=3,
                        style="product_photography"
                    )
                
                if images:
                    generated_images = images
                    listing_sessions[session_id]["generated_images"] = images
                    logger.info(f"✅ {len(images)} imágenes generadas exitosamente")
                else:
                    logger.warning("⚠️ No se pudieron generar imágenes")
                    
            except Exception as img_error:
                logger.error(f"❌ Error generando imágenes: {str(img_error)}")
                # Continuar sin fallar si hay error en generación de imágenes
            
            # Extraer prompts de imágenes si están disponibles
            image_ai_prompts = copywriter_data.get("image_ai_prompts", {})
            
            return {
                "success": True,
                "session_id": session_id,
                "listing": copywriter_data,
                "suggestions": suggestions,
                "generated_images": generated_images,
                "image_ai_prompts": image_ai_prompts,  # Incluir prompts de imágenes
                "confidence": copywriter_result.confidence,
                "agent": "amazon_copywriter_agent",
                "database_id": listing_sessions[session_id].get("database_id"),
                "auto_saved": listing_sessions[session_id].get("database_id") is not None
            }
        else:
            raise HTTPException(status_code=500, detail=f"Error en Copywriter agent: {copywriter_result.notes}")
            
    except Exception as e:
        logger.error(f"❌ Error generando listing: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/apply-suggestion")
async def apply_suggestion(request: SuggestionApplication):
    """Aplica una sugerencia al listing"""
    try:
        session_id = request.session_id  # Usar session_id del request
        
        if session_id not in listing_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = listing_sessions[session_id]
        content = request.edited_content if request.edited_content else request.content
        
        # Aplicar cambio según el campo
        if request.field == "title":
            session["current"]["main_title"] = content
        elif request.field == "bullets":
            # Buscar el índice del bullet en las sugerencias
            bullet_index = None
            for suggestion in session["suggestions"]:
                if suggestion["id"] == request.suggestion_id and "bullet_index" in suggestion:
                    bullet_index = suggestion["bullet_index"]
                    break
            
            if bullet_index is not None and "bullet_points" in session["current"]:
                if bullet_index < len(session["current"]["bullet_points"]):
                    session["current"]["bullet_points"][bullet_index] = content
        elif request.field == "description":
            session["current"]["product_description"] = content
        
        # Registrar sugerencia aplicada
        session["applied_suggestions"].append({
            "suggestion_id": request.suggestion_id,
            "field": request.field,
            "original_content": session["original"].get(request.field, ""),
            "applied_content": content,
            "timestamp": "now"  # Usar datetime real
        })
        
        return {
            "success": True,
            "updated_listing": session["current"],
            "applied_suggestions_count": len(session["applied_suggestions"])
        }
        
    except Exception as e:
        logger.error(f"❌ Error aplicando sugerencia: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/revert-changes/{session_id}")
async def revert_changes(session_id: str):
    """Revierte todos los cambios al estado original"""
    try:
        if session_id not in listing_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = listing_sessions[session_id]
        
        # Restaurar al estado original
        session["current"] = session["original"].copy()
        session["applied_suggestions"] = []
        
        return {
            "success": True,
            "reverted_listing": session["current"],
            "message": "Cambios revertidos exitosamente"
        }
        
    except Exception as e:
        logger.error(f"❌ Error revirtiendo cambios: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/apply-all-suggestions/{session_id}")
async def apply_all_suggestions(session_id: str):
    """Aplica todas las sugerencias de una vez"""
    try:
        if session_id not in listing_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = listing_sessions[session_id]
        applied_count = 0
        
        # Aplicar todas las sugerencias
        for suggestion in session["suggestions"]:
            if suggestion["field"] == "title":
                session["current"]["main_title"] = suggestion["content"]
            elif suggestion["field"] == "bullets":
                bullet_index = suggestion.get("bullet_index", 0)
                if "bullet_points" in session["current"]:
                    if bullet_index < len(session["current"]["bullet_points"]):
                        session["current"]["bullet_points"][bullet_index] = suggestion["content"]
            elif suggestion["field"] == "description":
                session["current"]["product_description"] = suggestion["content"]
            
            applied_count += 1
        
        # Registrar todas como aplicadas
        session["applied_suggestions"] = session["suggestions"].copy()
        
        return {
            "success": True,
            "updated_listing": session["current"],
            "applied_count": applied_count,
            "message": f"Se aplicaron {applied_count} sugerencias"
        }
        
    except Exception as e:
        logger.error(f"❌ Error aplicando todas las sugerencias: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/regenerate-suggestion")
async def regenerate_suggestion(request: SuggestionRegeneration):
    """Regenera una sugerencia específica usando el LLM correspondiente"""
    try:
        session_id = request.session_id
        
        if session_id not in listing_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = listing_sessions[session_id]
        
        # Buscar la sugerencia original
        original_suggestion = None
        for suggestion in session["suggestions"]:
            if suggestion["id"] == request.suggestion_id:
                original_suggestion = suggestion
                break
        
        if not original_suggestion:
            raise HTTPException(status_code=404, detail="Sugerencia no encontrada")
        
        # Generar nueva sugerencia usando el agente correspondiente
        agent_name = original_suggestion.get("agent", "auto_optimizer")
        
        if agent_name == "amazon_copywriter_agent" or request.field in ["title", "description", "bullets"]:
            # Usar Amazon Copywriter Agent para regenerar
            from ..agents.amazon_copywriter_agent import AmazonCopywriterAgent
            
            copywriter_agent = AmazonCopywriterAgent()
            
            # Crear prompt específico para regeneración
            regeneration_prompt = _create_regeneration_prompt(
                request.field, 
                request.current_content, 
                request.regeneration_type,
                session["original"],
                original_suggestion
            )
            
            # Generar nueva variación
            regeneration_response = await copywriter_agent.ollama_service.generate_structured_response(
                prompt=regeneration_prompt,
                expected_format="json",
                temperature=0.7  # Mayor creatividad para variaciones
            )
            
            if regeneration_response.get("success", False):
                new_content = regeneration_response["parsed_data"].get("new_content", request.current_content)
                reason = regeneration_response["parsed_data"].get("reason", "Contenido regenerado")
            else:
                # Fallback simple
                new_content = _generate_fallback_content(request.field, request.current_content, request.regeneration_type)
                reason = f"Variación {request.regeneration_type} generada"
        else:
            # Para otros agentes, generar variación simple
            new_content = _generate_fallback_content(request.field, request.current_content, request.regeneration_type)
            reason = f"Variación {request.regeneration_type} generada"
        
        # Actualizar la sugerencia en la sesión
        for i, suggestion in enumerate(session["suggestions"]):
            if suggestion["id"] == request.suggestion_id:
                session["suggestions"][i]["content"] = new_content
                session["suggestions"][i]["reason"] = reason
                session["suggestions"][i]["regenerated"] = True
                break
        
        return {
            "success": True,
            "new_content": new_content,
            "reason": reason,
            "updated_suggestions": session["suggestions"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error regenerando sugerencia: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def _create_regeneration_prompt(field: str, current_content: str, regeneration_type: str, 
                               original_listing: Dict[str, Any], original_suggestion: Dict[str, Any]) -> str:
    """Crea un prompt específico para regenerar contenido"""
    
    base_prompt = f"""
Eres un experto Amazon Copywriter. Tu tarea es REGENERAR y MEJORAR el siguiente contenido.

CONTENIDO ACTUAL A MEJORAR:
"{current_content}"

CAMPO: {field}
TIPO DE REGENERACIÓN: {regeneration_type}

CONTEXTO DEL PRODUCTO:
- Título original: {original_listing.get('main_title', 'N/A')}
- Descripción: {original_listing.get('product_description', 'N/A')[:200]}...

INSTRUCCIONES ESPECÍFICAS:
"""
    
    if regeneration_type == "improve":
        base_prompt += """
- Mantén el mensaje principal pero hazlo MÁS PERSUASIVO
- Añade power words más fuertes
- Incluye elementos de urgencia o escasez sutil
- Mejora el flow y la claridad
"""
    elif regeneration_type == "alternative":
        base_prompt += """
- Cambia completamente el enfoque manteniendo el beneficio
- Usa un ángulo diferente (problema diferente, beneficio diferente)
- Cambia el tono (más emocional, más técnico, más casual, etc.)
- Aplica un framework de copywriting diferente
"""
    elif regeneration_type == "shorter":
        base_prompt += """
- Reduce la longitud manteniendo el impacto
- Elimina palabras innecesarias
- Condensa el mensaje a lo esencial
- Mantén los elementos más persuasivos
"""
    elif regeneration_type == "longer":
        base_prompt += """
- Añade más detalles persuasivos
- Incluye más beneficios específicos
- Agrega elementos de prueba social
- Expande con ejemplos o casos de uso
"""
    
    if field == "title":
        base_prompt += """
REGLAS ESPECÍFICAS PARA TÍTULO:
- Máximo 200 caracteres
- Keyword principal en primeros 50 caracteres
- Incluir beneficio clave
- Mantener legibilidad
"""
    elif field == "bullets":
        base_prompt += """
REGLAS ESPECÍFICAS PARA BULLET POINTS:
- Máximo 255 caracteres
- Comenzar con BENEFICIO en MAYÚSCULAS
- Incluir característica que lo respalde
- Usar números específicos cuando sea posible
"""
    elif field == "description":
        base_prompt += """
REGLAS ESPECÍFICAS PARA DESCRIPCIÓN:
- Máximo 2000 caracteres
- Estructura clara con párrafos cortos
- Incluir call-to-action sutil
- Mantener persuasión emocional
"""
    
    base_prompt += """

RESPONDE EN FORMATO JSON:
{
  "new_content": "El contenido regenerado aquí",
  "reason": "Explicación breve de los cambios realizados",
  "improvements": ["Mejora 1", "Mejora 2", "Mejora 3"]
}

IMPORTANTE: El nuevo contenido debe ser NOTABLEMENTE diferente y mejor que el original.
"""
    
    return base_prompt

def _generate_fallback_content(field: str, current_content: str, regeneration_type: str) -> str:
    """Genera contenido fallback cuando el LLM no está disponible"""
    
    power_words = ["Premium", "Professional", "Advanced", "Ultimate", "Exclusive", "Superior"]
    
    if regeneration_type == "improve":
        # Añadir power word al inicio
        return f"{power_words[0]} {current_content}"
    elif regeneration_type == "alternative":
        # Cambiar enfoque
        if field == "title":
            return f"Nuevo Enfoque: {current_content}"
        else:
            return f"Descubre una nueva perspectiva: {current_content}"
    elif regeneration_type == "shorter":
        # Acortar manteniendo esencia
        words = current_content.split()
        return " ".join(words[:len(words)//2]) + "..."
    elif regeneration_type == "longer":
        # Expandir con beneficios
        return f"{current_content} - Garantía de satisfacción incluida para tu tranquilidad total."
    
    return current_content

async def _generate_suggestions(listing_data: Dict[str, Any], product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Genera sugerencias automáticas para mejorar el listing"""
    suggestions = []
    
    # Sugerencia para título - optimizar longitud
    if "main_title" in listing_data:
        title = listing_data["main_title"]
        if len(title) < 150:  # Amazon permite hasta 200
            suggestions.append({
                "id": "title_length_opt",
                "field": "title",
                "type": "optimization",
                "content": f"{title} - Premium Quality for {product_data.get('category', 'All Needs')}",
                "reason": "Optimizar longitud del título para mejor SEO",
                "agent": "auto_optimizer",
                "priority": "medium"
            })
    
    # Sugerencias para bullet points - añadir beneficios
    if "bullet_points" in listing_data:
        bullets = listing_data["bullet_points"]
        for i, bullet in enumerate(bullets[:3]):  # Solo primeros 3
            if len(bullet) < 200:  # Amazon permite 255
                suggestions.append({
                    "id": f"bullet_{i}_enhance",
                    "field": "bullets",
                    "bullet_index": i,
                    "type": "enhancement",
                    "content": f"{bullet} - Garantía de satisfacción incluida",
                    "reason": f"Mejorar bullet point {i+1} con garantía de valor",
                    "agent": "auto_optimizer",
                    "priority": "low"
                })
    
    # Sugerencia para descripción - añadir call to action
    if "product_description" in listing_data:
        description = listing_data["product_description"]
        if "compra" not in description.lower() and "ordena" not in description.lower():
            suggestions.append({
                "id": "desc_cta",
                "field": "description",
                "type": "enhancement",
                "content": f"{description}\n\n¡Ordena ahora y experimenta la diferencia! Tu satisfacción es nuestra garantía.",
                "reason": "Añadir call-to-action para mejorar conversión",
                "agent": "auto_optimizer",
                "priority": "high"
            })
    
    return suggestions


# === ENDPOINT PARA GUARDAR LISTING ===

@router.post("/api/save-listing")
async def save_listing(request: SaveListingRequest, db: AsyncSession = Depends(get_db)):
    """Guarda el listing actual de la sesión en la base de datos"""
    try:
        session_id = request.session_id
        
        if session_id not in listing_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = listing_sessions[session_id]
        
        # Si ya tiene database_id, significa que ya está guardado
        if session.get("database_id"):
            logger.info(f"📝 Listing ya guardado con ID: {session['database_id']}")
            return {
                "success": True,
                "message": "Listing ya estaba guardado",
                "database_id": session["database_id"],
                "already_saved": True
            }
        
        # Obtener datos actuales del listing (con cambios aplicados si los hay)
        current_listing = session.get("current", {})
        product_data = session.get("product_data", {})
        
        logger.info(f"💾 Intentando guardar listing para sesión: {session_id}")
        
        # Usar el mismo método que el auto-save pero con los datos actuales
        try:
            from ..models import ProcessedListing, CustomerProfile, TechnicalSpecs, BoxContents, PricingStrategy, SEOKeywords, VisualAssets, AgentResponse
            
            # Crear estructuras de datos necesarias
            customer_profile = CustomerProfile(
                age_range="25-45",
                gender=None,
                interests=["Technology", "Quality products"],
                pain_points=["Need for reliable products"],
                use_cases=current_listing.get("use_situations", ["General use"])
            )
            
            technical_specs = TechnicalSpecs(
                dimensions=current_listing.get("dimensions"),
                weight=current_listing.get("weight"),
                materials=current_listing.get("materials", "").split(",") if current_listing.get("materials") else [],
                compatibility=current_listing.get("compatibility", "").split(",") if current_listing.get("compatibility") else [],
                technical_requirements=[]
            )
            
            box_contents = BoxContents(
                main_product=product_data.get("product_name", ""),
                accessories=current_listing.get("box_content", []) if isinstance(current_listing.get("box_content"), list) else [],
                documentation=["User manual", "Warranty card"],
                warranty_info="Standard warranty included",
                certifications=[]
            )
            
            pricing_strategy = PricingStrategy(
                initial_price=0.0,
                competitor_price_range={"min": 0.0, "max": 100.0},
                promotional_strategy=["Standard promotions"],
                discount_structure={"standard": 0.10}
            )
            
            seo_keywords = SEOKeywords(
                primary_keywords=product_data.get("target_keywords", [])[:3] if len(product_data.get("target_keywords", [])) >= 3 else product_data.get("target_keywords", []),
                secondary_keywords=product_data.get("target_keywords", [])[3:] if len(product_data.get("target_keywords", [])) > 3 else [],
                long_tail_keywords=current_listing.get("search_terms", []) if isinstance(current_listing.get("search_terms"), list) else [],
                search_terms=current_listing.get("search_terms", product_data.get("target_keywords", [])) if isinstance(current_listing.get("search_terms"), list) else product_data.get("target_keywords", []),
                backend_keywords=current_listing.get("backend_keywords", []) if isinstance(current_listing.get("backend_keywords"), list) else []
            )
            
            visual_assets = VisualAssets(
                product_photos=[],
                lifestyle_photos=[],
                infographics=[],
                renders=[],
                video_urls=[]
            )
            
            # Crear el ProcessedListing con los datos actuales
            processed_listing = ProcessedListing(
                product_analysis={
                    "category": product_data.get("category", ""),
                    "brand": product_data.get("brand", ""),
                    "main_features": current_listing.get("bullet_points", []) if isinstance(current_listing.get("bullet_points"), list) else [],
                    "competitive_advantages": current_listing.get("competitive_advantages", [])
                },
                customer_research=customer_profile,
                value_proposition_analysis={
                    "core_benefits": current_listing.get("value_proposition", ""),
                    "unique_selling_points": (current_listing.get("bullet_points", []) if isinstance(current_listing.get("bullet_points"), list) else [])[:3]
                },
                technical_specifications=technical_specs,
                box_contents=box_contents,
                pricing_strategy=pricing_strategy,
                seo_keywords=seo_keywords,
                visual_assets=visual_assets,
                title=current_listing.get("main_title", product_data.get("product_name", "")),
                bullet_points=current_listing.get("bullet_points", []) if isinstance(current_listing.get("bullet_points"), list) else [],
                description=current_listing.get("product_description", product_data.get("value_proposition", "")),
                search_terms=current_listing.get("search_terms", product_data.get("target_keywords", [])) if isinstance(current_listing.get("search_terms"), list) else product_data.get("target_keywords", []),
                backend_keywords=current_listing.get("backend_keywords", []) if isinstance(current_listing.get("backend_keywords"), list) else [],
                images_order=[],
                a_plus_content=json.dumps(current_listing.get("a_plus_content")) if isinstance(current_listing.get("a_plus_content"), dict) else current_listing.get("a_plus_content"),
                confidence_score=0.8,  # Default confidence
                processing_notes=[f"Saved manually from session {session_id}"],
                recommendations=[],
                metadata={
                    "generation_timestamp": datetime.now().isoformat(),
                    "agent_used": "manual_save",
                    "session_id": session_id,
                    "original_input": product_data,
                    "current_data": current_listing
                }
            )
            
            # Guardar usando el servicio de listing
            from ..services.listing_service import ListingService
            listing_service = ListingService(db)
            
            # Crear ProductInput para el servicio
            product_input = ProductInput(
                product_name=product_data.get("product_name", ""),
                category=ProductCategory.ELECTRONICS,  # Mapear categoría apropiadamente
                value_proposition=product_data.get("value_proposition", ""),
                target_keywords=product_data.get("target_keywords", []),
                competitive_advantages=[],
                use_situations=[],
                target_price=0.0,
                target_customer_description="",
                pricing_strategy_notes="",
                raw_specifications="",
                box_content_description="",
                warranty_info="",
                certifications=[]
            )
            
            # Crear respuesta de agente
            agent_response_obj = AgentResponse(
                agent_name="manual_save",
                status="success",
                data=current_listing,
                confidence=0.8,
                processing_time=0.0,
                notes=[f"Saved manually from session {session_id}"]
            )
            
            agent_responses = {
                "manual_save": agent_response_obj
            }
            
            db_listing = await listing_service.create_listing(
                product_input, 
                processed_listing, 
                agent_responses
            )
            
            # Actualizar sesión con ID de base de datos
            session["database_id"] = db_listing.id
            logger.info(f"✅ Listing guardado manualmente en base de datos con ID: {db_listing.id}")
            
            return {
                "success": True,
                "message": "Listing guardado exitosamente",
                "database_id": db_listing.id,
                "saved_manually": True
            }
            
        except Exception as save_error:
            logger.error(f"❌ Error guardando en base de datos: {str(save_error)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error guardando en base de datos: {str(save_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en save_listing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# === ENDPOINTS PARA GENERACIÓN DE IMÁGENES ===

class ImageGenerationRequest(BaseModel):
    product_name: str
    description: str
    num_images: Optional[int] = 3
    style: Optional[str] = "product_photography"

@router.post("/api/generate-images")
async def generate_product_images(request: ImageGenerationRequest):
    """Genera imágenes para un producto usando Stable Diffusion"""
    try:
        logger.info(f"🎨 Generando imágenes para: {request.product_name}")
        
        image_service = get_image_generation_service()
        
        images = await image_service.generate_product_images(
            product_name=request.product_name,
            description=request.description,
            num_images=request.num_images or 3,
            style=request.style or "product_photography"
        )
        
        if images:
            logger.info(f"✅ {len(images)} imágenes generadas")
            return {"success": True, "images": images, "total_generated": len(images)}
        else:
            return {"success": False, "error": "No se pudieron generar imágenes", "images": []}
            
    except Exception as e:
        logger.error(f"❌ Error generando imágenes: {str(e)}")
        return {"success": False, "error": str(e), "images": []}

@router.get("/api/generated-images")
async def get_generated_images():
    """Obtiene la lista de todas las imágenes generadas"""
    try:
        image_service = get_image_generation_service()
        images_info = image_service.get_generated_images_info()
        
        return {"success": True, "images": images_info, "total": len(images_info)}
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo imágenes: {str(e)}")
        return {"success": False, "error": str(e), "images": []}

@router.get("/api/session-images/{session_id}")
async def get_session_images(session_id: str):
    """Obtiene todas las imágenes de una sesión específica"""
    try:
        if session_id not in listing_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = listing_sessions[session_id]
        images = session.get("generated_images", [])
        
        return {"success": True, "session_id": session_id, "images": images, "total": len(images)}
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo imágenes de sesión: {str(e)}")
        return {"success": False, "error": str(e), "images": []}
