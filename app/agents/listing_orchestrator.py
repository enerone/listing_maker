import asyncio
from typing import Dict, Any, List
import logging
from datetime import datetime

from .product_analysis_agent import ProductAnalysisAgent
from .customer_research_agent import CustomerResearchAgent
from .value_proposition_agent import ValuePropositionAgent
from .technical_specs_agent import TechnicalSpecsAgent
from .content_agent import ContentAgent
from .product_description_agent import ProductDescriptionAgent
from .pricing_strategy_agent import PricingStrategyAgent
from .seo_visual_agent import SEOVisualAgent
from .competitive_analysis_agent import CompetitiveAnalysisAgent
from .social_content_agent import SocialContentAgent
from .marketing_review_agent import MarketingReviewAgent
from .image_search_agent import ImageSearchAgent
from .amazon_copywriter_agent import AmazonCopywriterAgent
from ..models import (
    ProductInput, ProcessedListing, AgentResponse,
    CustomerProfile, TechnicalSpecs, BoxContents, 
    PricingStrategy, SEOKeywords, VisualAssets
)

logger = logging.getLogger(__name__)

class ListingOrchestrator:
    """
    Orquestador principal que coordina todos los agentes para crear listings completos
    """
    
    def __init__(self):
        self.agents = {
            "product_analysis": ProductAnalysisAgent(),
            "customer_research": CustomerResearchAgent(),
            "value_proposition": ValuePropositionAgent(),
            "technical_specs": TechnicalSpecsAgent(),
            "content": ContentAgent(),
            "product_description": ProductDescriptionAgent(),
            "pricing_strategy": PricingStrategyAgent(),
            "seo_visual": SEOVisualAgent(),
            "competitive_analysis": CompetitiveAnalysisAgent(),
            "social_content": SocialContentAgent(),
            "marketing_review": MarketingReviewAgent(),
            "image_search": ImageSearchAgent(),
            "amazon_copywriter": AmazonCopywriterAgent(),
        }
        self._last_agent_responses = {}  # Almacenar última ejecución
        
    async def create_listing(self, product_input: ProductInput) -> ProcessedListing:
        """
        Procesa un producto a través de todos los agentes y genera un listing completo
        """
        start_time = datetime.now()
        
        try:
            # Ejecutar agentes en paralelo (todos son independientes por ahora)
            logger.info("Iniciando análisis con todos los agentes especializados...")
            
            all_tasks = {
                "product_analysis": self.agents["product_analysis"].process(product_input),
                "customer_research": self.agents["customer_research"].process(product_input),
                "value_proposition": self.agents["value_proposition"].process(product_input),
                "technical_specs": self.agents["technical_specs"].process(product_input),
                "content": self.agents["content"].process(product_input),
                "pricing_strategy": self.agents["pricing_strategy"].process(product_input),
                "seo_visual": self.agents["seo_visual"].process(product_input),
                "competitive_analysis": self.agents["competitive_analysis"].process(product_input),
                "social_content": self.agents["social_content"].process(product_input),
                "product_description": self.agents["product_description"].process(product_input),
                "amazon_copywriter": self.agents["amazon_copywriter"].process(product_input),
            }
            
            all_results = await asyncio.wait_for(
                asyncio.gather(
                    *all_tasks.values(),
                    return_exceptions=True
                ),
                timeout=120.0  # Timeout de 2 minutos para todos los agentes
            )
            
            # Procesar resultados de todos los agentes
            agent_responses = {}
            for agent_name, result in zip(all_tasks.keys(), all_results):
                if isinstance(result, Exception):
                    logger.error(f"Error en agente {agent_name}: {str(result)}")
                    agent_responses[agent_name] = self._create_error_response(agent_name, str(result))
                else:
                    agent_responses[agent_name] = result
            
            # Generar listing final con todos los datos
            listing = await self._generate_final_listing(product_input, agent_responses)
            
            # PASO FINAL: Ejecutar Marketing Review Agent para optimizar el listing
            logger.info("Ejecutando Marketing Review Agent para optimización final...")
            try:
                marketing_review_data = {
                    "product_data": product_input.dict(),
                    "previous_results": {name: resp.data for name, resp in agent_responses.items() if resp.status == "success"}
                }
                
                marketing_review_result = await self.agents["marketing_review"].process(marketing_review_data)
                agent_responses["marketing_review"] = marketing_review_result
                
                # Aplicar las mejoras sugeridas por el marketing review al listing
                if marketing_review_result.get("success") and marketing_review_result.get("data"):
                    listing = await self._apply_marketing_improvements(listing, marketing_review_result["data"])
                    logger.info("Mejoras de marketing aplicadas al listing")
                else:
                    logger.warning("Marketing Review Agent no pudo ejecutarse correctamente")
                    
            except Exception as e:
                logger.error(f"Error en Marketing Review Agent: {e}. Continuando con listing original.")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Listing generado exitosamente en {processing_time:.2f} segundos")
            
            # Almacenar respuestas de agentes
            self._last_agent_responses = agent_responses
            
            return listing
            
        except Exception as e:
            logger.error(f"Error en orquestación: {str(e)}")
            raise
    
    async def _generate_final_listing(
        self, 
        product_input: ProductInput, 
        agent_responses: Dict[str, AgentResponse]
    ) -> ProcessedListing:
        """
        Genera el listing final basado en las respuestas de todos los agentes
        """
        try:
            # Calcular confidence score promedio
            confidence_scores = [
                resp.confidence for resp in agent_responses.values() 
                if resp.status == "success"
            ]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            # Extraer datos procesados por cada agente de forma segura
            def safe_get_data(agent_name: str) -> Dict[str, Any]:
                agent_response = agent_responses.get(agent_name)
                return agent_response.data if agent_response and agent_response.status == "success" else {}
            
            product_analysis_data = safe_get_data("product_analysis")
            customer_data = safe_get_data("customer_research")
            value_prop_data = safe_get_data("value_proposition")
            technical_data = safe_get_data("technical_specs")
            content_data = safe_get_data("content")
            pricing_data = safe_get_data("pricing_strategy")
            seo_data = safe_get_data("seo_visual")
            # competitive_data = safe_get_data("competitive_analysis")  # Para uso futuro
            # social_data = safe_get_data("social_content")  # Para uso futuro
            copywriter_data = safe_get_data("amazon_copywriter")
            
            # Crear objetos Pydantic con datos por defecto si no están disponibles
            customer_profile = CustomerProfile(
                age_range=customer_data.get("target_demographics", {}).get("age_range", "25-45"),
                gender=customer_data.get("target_demographics", {}).get("gender"),
                interests=customer_data.get("target_demographics", {}).get("interests", []),
                pain_points=customer_data.get("target_demographics", {}).get("pain_points", []),
                use_cases=customer_data.get("use_cases", product_input.use_situations)
            )
            
            technical_specs = TechnicalSpecs(
                dimensions=technical_data.get("main_specifications", {}).get("dimensions"),
                weight=technical_data.get("main_specifications", {}).get("weight"),
                materials=technical_data.get("main_specifications", {}).get("materials", []),
                compatibility=technical_data.get("compatibility", {}).get("devices", []),
                technical_requirements=technical_data.get("compatibility", {}).get("requirements", [])
            )
            
            box_contents = BoxContents(
                main_product=content_data.get("box_contents", {}).get("main_product", product_input.product_name),
                accessories=content_data.get("box_contents", {}).get("accessories", []),
                documentation=content_data.get("box_contents", {}).get("documentation", []),
                warranty_info=content_data.get("warranty_info", {}).get("warranty_coverage", product_input.warranty_info),
                certifications=content_data.get("certifications", {}).get("quality_certifications", product_input.certifications)
            )
            
            pricing_strategy = PricingStrategy(
                initial_price=pricing_data.get("price_analysis", {}).get("target_price", product_input.target_price),
                competitor_price_range=pricing_data.get("competitive_strategy", {}).get("estimated_competitor_range", {"min": 0.0, "max": 0.0}),
                promotional_strategy=pricing_data.get("launch_strategy", {}).get("promotional_phases", []),
                discount_structure=pricing_data.get("promotion_structure", {}).get("early_bird_discount", {})
            )
            
            # Generar keywords para búsqueda
            search_terms = self._extract_search_terms(product_input, product_analysis_data)
            backend_keywords = self._extract_backend_keywords(product_input, product_analysis_data)
            
            seo_keywords = SEOKeywords(
                primary_keywords=seo_data.get("seo_strategy", {}).get("primary_keywords", product_input.target_keywords[:3]),
                secondary_keywords=seo_data.get("seo_strategy", {}).get("secondary_keywords", product_input.target_keywords[3:]),
                long_tail_keywords=seo_data.get("seo_strategy", {}).get("long_tail_keywords", []),
                search_terms=seo_data.get("search_terms_optimization", {}).get("frontend_terms", product_input.target_keywords),
                backend_keywords=backend_keywords
            )
            
            visual_assets = VisualAssets(
                product_photos=product_input.available_assets[:5] if product_input.available_assets else [],
                lifestyle_photos=[],
                infographics=[],
                renders=[],
                video_urls=[]
            )
            
            # Generar título optimizado (usar copywriter si está disponible)
            title = self._get_optimized_title(product_input, product_analysis_data, copywriter_data)
            
            # Generar bullet points (usar copywriter si está disponible)
            bullet_points = self._get_optimized_bullet_points(product_input, value_prop_data, customer_data, copywriter_data)
            
            # Generar descripción (usar copywriter si está disponible)
            description = self._get_optimized_description(product_input, agent_responses, copywriter_data)
            
            # Recolectar recomendaciones de todos los agentes
            all_recommendations = []
            processing_notes = []
            
            for agent_name, response in agent_responses.items():
                if response.recommendations:
                    all_recommendations.extend([f"[{agent_name}] {rec}" for rec in response.recommendations])
                if response.notes:
                    processing_notes.extend([f"[{agent_name}] {note}" for note in response.notes])
            
            # Crear el listing procesado
            listing = ProcessedListing(
                # Datos procesados por agentes
                product_analysis=product_analysis_data,
                customer_research=customer_profile,
                value_proposition_analysis=value_prop_data,
                technical_specifications=technical_specs,
                box_contents=box_contents,
                pricing_strategy=pricing_strategy,
                seo_keywords=seo_keywords,
                visual_assets=visual_assets,
                
                # Listing final
                title=title,
                bullet_points=bullet_points,
                description=description,
                search_terms=search_terms,
                backend_keywords=backend_keywords,
                images_order=seo_data.get("image_strategy", {}).get("secondary_images_plan", [])[:7],
                a_plus_content=seo_data.get("a_plus_content_strategy", {}).get("visual_storytelling"),
                
                # Metadatos
                confidence_score=avg_confidence,
                processing_notes=processing_notes,
                recommendations=all_recommendations
            )
            
            return listing
            
        except Exception as e:
            logger.error(f"Error generando listing final: {str(e)}")
            raise
    
    def _get_optimized_title(self, product_input: ProductInput, product_analysis_data: Dict, copywriter_data: Dict) -> str:
        """
        Genera un título optimizado usando el agente de Amazon Copywriter si está disponible
        """
        try:
            # Si el copywriter generó un título, usarlo
            if copywriter_data and copywriter_data.get("main_title"):
                title = copywriter_data["main_title"]
                logger.info(f"Usando título del Amazon Copywriter: {title[:50]}...")
                return title
            
            # Fallback: generar título básico
            logger.info("Generando título básico (copywriter no disponible)")
            return self._generate_basic_title(product_input, product_analysis_data)
            
        except Exception as e:
            logger.warning(f"Error obteniendo título optimizado: {str(e)}")
            return self._generate_basic_title(product_input, product_analysis_data)
    
    def _get_optimized_bullet_points(self, product_input: ProductInput, value_prop_data: Dict, customer_data: Dict, copywriter_data: Dict) -> List[str]:
        """
        Genera bullet points optimizados usando el agente de Amazon Copywriter si está disponible
        """
        try:
            # Si el copywriter generó bullet points, usarlos
            if copywriter_data and copywriter_data.get("bullet_points"):
                bullet_points = copywriter_data["bullet_points"]
                if isinstance(bullet_points, list) and len(bullet_points) > 0:
                    logger.info(f"Usando {len(bullet_points)} bullet points del Amazon Copywriter")
                    return bullet_points[:5]  # Máximo 5 bullet points
            
            # Fallback: generar bullet points básicos
            logger.info("Generando bullet points básicos (copywriter no disponible)")
            return self._generate_basic_bullet_points(product_input, value_prop_data, customer_data)
            
        except Exception as e:
            logger.warning(f"Error obteniendo bullet points optimizados: {str(e)}")
            return self._generate_basic_bullet_points(product_input, value_prop_data, customer_data)
    
    def _get_optimized_description(self, product_input: ProductInput, agent_responses: Dict, copywriter_data: Dict) -> str:
        """
        Genera descripción optimizada usando el agente de Amazon Copywriter si está disponible
        """
        try:
            # Si el copywriter generó una descripción, usarla
            if copywriter_data and copywriter_data.get("product_description"):
                description = copywriter_data["product_description"]
                logger.info(f"Usando descripción del Amazon Copywriter ({len(description)} caracteres)")
                return description
            
            # Fallback: generar descripción básica
            logger.info("Generando descripción básica (copywriter no disponible)")
            return self._generate_basic_description(product_input, agent_responses)
            
        except Exception as e:
            logger.warning(f"Error obteniendo descripción optimizada: {str(e)}")
            return self._generate_basic_description(product_input, agent_responses)
    
    def _generate_basic_title(self, product_input: ProductInput, product_analysis_data: Dict) -> str:
        """
        Genera un título básico cuando el copywriter no está disponible
        """
        try:
            # Usar el análisis del producto si está disponible
            optimized_name = product_analysis_data.get("product_name_analysis", {}).get("optimized_name", product_input.product_name)
            
            # Estructura básica: Nombre + Características clave
            title_parts = [optimized_name]
            
            # Agregar características clave si están disponibles
            if product_input.competitive_advantages:
                key_features = product_input.competitive_advantages[:2]  # Máximo 2 características
                title_parts.extend(key_features)
            
            title = " - ".join(title_parts)
            
            # Limitar a 200 caracteres (límite de Amazon)
            if len(title) > 200:
                title = title[:197] + "..."
            
            return title
            
        except Exception as e:
            logger.warning(f"Error generando título básico: {str(e)}")
            return product_input.product_name
    
    def _generate_basic_bullet_points(self, product_input: ProductInput, value_prop_data: Dict, customer_data: Dict) -> List[str]:
        """
        Genera bullet points básicos cuando el copywriter no está disponible
        """
        try:
            bullet_points = []
            
            # 1. Beneficio principal de la propuesta de valor
            if value_prop_data.get("core_value_proposition"):
                bullet_points.append(f"✓ {value_prop_data['core_value_proposition']}")
            elif product_input.value_proposition:
                bullet_points.append(f"✓ {product_input.value_proposition}")
            
            # 2. Ventajas competitivas
            for advantage in product_input.competitive_advantages[:2]:  # Máximo 2
                bullet_points.append(f"✓ {advantage}")
            
            # 3. Casos de uso principales
            if product_input.use_situations:
                bullet_points.append(f"✓ Ideal para: {', '.join(product_input.use_situations[:3])}")
            
            # 4. Información técnica clave
            if product_input.raw_specifications:
                bullet_points.append(f"✓ Especificaciones: {product_input.raw_specifications[:100]}...")
            
            # 5. Garantía o soporte
            if product_input.warranty_info:
                bullet_points.append(f"✓ Garantía: {product_input.warranty_info}")
            elif product_input.certifications:
                bullet_points.append(f"✓ Certificado: {', '.join(product_input.certifications[:2])}")
            
            # Asegurar que tengamos al menos 3 bullet points
            while len(bullet_points) < 3:
                if len(bullet_points) == 0:
                    bullet_points.append(f"✓ {product_input.product_name} - Calidad superior")
                elif len(bullet_points) == 1:
                    bullet_points.append("✓ Diseño premium y materiales de alta calidad")
                else:
                    bullet_points.append("✓ Fácil de usar y configurar")
            
            return bullet_points[:5]  # Máximo 5 bullet points
            
        except Exception as e:
            logger.warning(f"Error generando bullet points básicos: {str(e)}")
            return [
                f"✓ {product_input.product_name} - Producto de calidad",
                "✓ Diseño premium y duradero",
                "✓ Fácil de usar y configurar",
                "✓ Ideal para uso diario",
                "✓ Incluye soporte y garantía"
            ]
    
    def _generate_basic_description(self, product_input: ProductInput, agent_responses: Dict) -> str:
        """
        Genera descripción básica cuando el copywriter no está disponible
        """
        try:
            description_parts = []
            
            # Introducción
            description_parts.append(f"Descubre el {product_input.product_name}, diseñado para ofrecerte la mejor experiencia.")
            
            # Propuesta de valor
            if product_input.value_proposition:
                description_parts.append(f"\n{product_input.value_proposition}")
            
            # Beneficios principales
            if product_input.competitive_advantages:
                description_parts.append("\nCARACTERÍSTICAS DESTACADAS:")
                for advantage in product_input.competitive_advantages[:4]:
                    description_parts.append(f"• {advantage}")
            
            # Casos de uso
            if product_input.use_situations:
                description_parts.append(f"\nPERFECTO PARA: {', '.join(product_input.use_situations)}")
            
            # Especificaciones técnicas
            if product_input.raw_specifications:
                description_parts.append(f"\nESPECIFICACIONES: {product_input.raw_specifications}")
            
            # Contenido de la caja
            if product_input.box_content_description:
                description_parts.append(f"\nINCLUYE: {product_input.box_content_description}")
            
            # Garantía
            if product_input.warranty_info:
                description_parts.append(f"\nGARANTÍA: {product_input.warranty_info}")
            
            description = "\n".join(description_parts)
            
            # Limitar a 2000 caracteres (límite de Amazon)
            if len(description) > 2000:
                description = description[:1997] + "..."
            
            return description
            
        except Exception as e:
            logger.warning(f"Error generando descripción básica: {str(e)}")
            return f"{product_input.product_name}\n\n{product_input.value_proposition}"
    
    def _extract_search_terms(self, product_input: ProductInput, product_analysis: Dict) -> List[str]:
        """
        Extrae términos de búsqueda relevantes
        """
        search_terms = set()
        
        # Keywords proporcionados por el usuario
        search_terms.update(product_input.target_keywords)
        
        # Nombre del producto y variaciones
        search_terms.add(product_input.product_name.lower())
        
        # Categoría
        search_terms.add(str(product_input.category).lower().replace("_", " "))
        
        return list(search_terms)[:10]  # Limitar a 10 términos principales
    
    def _extract_backend_keywords(self, product_input: ProductInput, product_analysis: Dict) -> List[str]:
        """
        Extrae keywords para backend de Amazon
        """
        backend_keywords = set()
        
        # Todas las keywords objetivo
        backend_keywords.update(product_input.target_keywords)
        
        # Sinónimos y variaciones del nombre
        product_words = product_input.product_name.lower().split()
        backend_keywords.update(product_words)
        
        # Beneficios como keywords
        for advantage in product_input.competitive_advantages:
            words = advantage.lower().split()
            backend_keywords.update([word for word in words if len(word) > 3])
        
        return list(backend_keywords)[:20]  # Amazon permite hasta 250 caracteres
    
    def _create_error_response(self, agent_name: str, error_msg: str) -> AgentResponse:
        """
        Crea una respuesta de error estándar para agentes que fallaron
        """
        return AgentResponse(
            agent_name=agent_name,
            status="error",
            data={},
            confidence=0.0,
            processing_time=0.0,
            notes=[f"Error: {error_msg}"],
            recommendations=[f"Revisar configuración del agente {agent_name}"]
        )
    
    async def get_last_agent_responses(self) -> Dict[str, AgentResponse]:
        """
        Retorna las respuestas de agentes de la última ejecución
        """
        return self._last_agent_responses
    
    async def _apply_marketing_improvements(self, listing: ProcessedListing, marketing_data: Dict[str, Any]) -> ProcessedListing:
        """
        Aplica las mejoras sugeridas por el Marketing Review Agent al listing final.
        """
        try:
            logger.info("Aplicando mejoras de marketing al listing...")
            
            # Obtener mejoras recomendadas
            mejoras = marketing_data.get("mejoras_recomendadas", {})
            
            # 1. Optimizar título si hay uno mejorado
            titulo_optimizado = mejoras.get("titulo_optimizado", {})
            if titulo_optimizado.get("nuevo_titulo") and titulo_optimizado["nuevo_titulo"].strip():
                nuevo_titulo = titulo_optimizado["nuevo_titulo"]
                logger.info(f"Aplicando título optimizado: {nuevo_titulo[:50]}...")
                listing.title = nuevo_titulo
            
            # 2. Mejorar descripción si hay una nueva
            descripcion_mejorada = mejoras.get("descripcion_mejorada", {})
            if descripcion_mejorada.get("nueva_descripcion") and descripcion_mejorada["nueva_descripcion"].strip():
                nueva_descripcion = descripcion_mejorada["nueva_descripcion"]
                logger.info("Aplicando descripción optimizada...")
                listing.description = nueva_descripcion
            
            # 3. Actualizar bullet points si hay optimizados
            bullets_optimizados = mejoras.get("bullet_points_optimizados", [])
            if bullets_optimizados and len(bullets_optimizados) > 0:
                nuevos_bullets = []
                for bullet_data in bullets_optimizados:
                    if isinstance(bullet_data, dict) and bullet_data.get("bullet"):
                        nuevos_bullets.append(bullet_data["bullet"])
                    elif isinstance(bullet_data, str):
                        nuevos_bullets.append(bullet_data)
                
                if nuevos_bullets:
                    logger.info(f"Aplicando {len(nuevos_bullets)} bullet points optimizados...")
                    listing.bullet_points = nuevos_bullets[:5]  # Máximo 5 bullet points
            
            # 4. Agregar keywords adicionales al SEO
            keywords_adicionales = mejoras.get("keywords_adicionales", {})
            nuevas_keywords = []
            
            # Keywords de alta conversión
            if keywords_adicionales.get("alta_conversion"):
                nuevas_keywords.extend(keywords_adicionales["alta_conversion"])
            
            # Long tail keywords
            if keywords_adicionales.get("long_tail"):
                nuevas_keywords.extend(keywords_adicionales["long_tail"])
            
            # Keywords semánticas
            if keywords_adicionales.get("semanticas"):
                nuevas_keywords.extend(keywords_adicionales["semanticas"])
            
            # Agregar nuevas keywords a las existentes (sin duplicados)
            if nuevas_keywords:
                keywords_existentes = set(listing.seo_keywords.search_terms)
                keywords_nuevas_unicas = [kw for kw in nuevas_keywords if kw not in keywords_existentes]
                
                if keywords_nuevas_unicas:
                    logger.info(f"Agregando {len(keywords_nuevas_unicas)} keywords adicionales...")
                    listing.seo_keywords.search_terms.extend(keywords_nuevas_unicas)
                    
                    # También agregar a backend keywords si hay espacio
                    backend_existentes = set(listing.seo_keywords.backend_keywords)
                    backend_nuevas = [kw for kw in keywords_nuevas_unicas[:10] if kw not in backend_existentes]
                    if backend_nuevas:
                        listing.seo_keywords.backend_keywords.extend(backend_nuevas)
            
            # 5. Aplicar estrategia de precio si se recomienda
            estrategia_precio = mejoras.get("estrategia_precio", {})
            if estrategia_precio.get("recomendacion"):
                logger.info("Nota de estrategia de precio registrada para revisión manual")
                # No modificamos el precio automáticamente, solo registramos la recomendación
            
            # 6. Agregar metadata de marketing review
            marketing_metadata = {
                "marketing_review_applied": True,
                "puntuacion_general": marketing_data.get("puntuacion_general", 0),
                "confidence_score": marketing_data.get("confidence_score", 0),
                "prioridades_implementacion": marketing_data.get("prioridades_implementacion", []),
                "timestamp": datetime.now().isoformat()
            }
            
            # Si no existe metadata, crearla
            if not hasattr(listing, 'metadata') or listing.metadata is None:
                listing.metadata = {}
            
            listing.metadata.update(marketing_metadata)
            
            logger.info("✅ Mejoras de marketing aplicadas exitosamente")
            return listing
            
        except Exception as e:
            logger.error(f"Error aplicando mejoras de marketing: {e}")
            # Retornar listing original si hay error
            return listing
