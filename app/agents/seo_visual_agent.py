from typing import Dict, Any
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class SEOVisualAgent(BaseAgent):
    """
    Agente especializado en optimización SEO y gestión de activos visuales.
    
    Responsabilidades:
    - Optimizar keywords para búsqueda en Amazon
    - Desarrollar estrategia de términos de búsqueda
    - Analizar y organizar activos visuales disponibles
    - Generar recomendaciones para imágenes y contenido visual
    """
    
    def __init__(self, temperature: float = 0.4):
        super().__init__(
            agent_name="SEO & Visual Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de SEO y visual
        """
        return """Eres un experto en SEO para Amazon y optimización de contenido visual. 
Tu trabajo es maximizar la visibilidad del producto en búsquedas y optimizar la presentación visual.
Entiendes el algoritmo A9 de Amazon y las mejores prácticas de conversión visual.
Siempre devuelves respuestas en formato JSON válido.
Eres estratégico, orientado a resultados y entiendes el comportamiento del comprador online.
IMPORTANTE: Todas las recomendaciones deben estar completamente en español, con un lenguaje claro y específico para el mercado hispanohablante."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Optimiza SEO y analiza activos visuales para el producto
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análisis SEO y visual para: {product_input.product_name}")
            
            # Preparar prompt especializado para SEO y visual
            prompt = self._build_seo_visual_prompt(product_input)
            
            # Generar respuesta con Ollama
            ollama_response = await self._generate_response(prompt, structured=True)
            
            # Extraer datos parseados
            if ollama_response.get("success") and ollama_response.get("is_structured"):
                parsed_response = ollama_response["parsed_data"]
            else:
                logger.error(f"Error en respuesta de Ollama: {ollama_response.get('error', 'Respuesta no estructurada')}")
                raise Exception(f"Error generando respuesta SEO: {ollama_response.get('error', 'Respuesta no válida')}")
            
            processing_time = time.time() - start_time
            
            # Crear respuesta del agente
            response = AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data=parsed_response,
                confidence=self._calculate_seo_confidence(parsed_response),
                processing_time=processing_time,
                notes=[
                    "Keywords principales identificadas",
                    "Estrategia SEO para Amazon desarrollada",
                    "Activos visuales analizados",
                    "Recomendaciones de contenido visual generadas"
                ],
                recommendations=parsed_response.get("recommendations", [])
            )
            
            logger.info(f"Análisis SEO y visual completado con confianza: {response.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error en análisis SEO y visual: {str(e)}")
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                data={},
                confidence=0.0,
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"]
            )
    
    def _build_seo_visual_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt especializado para SEO y visual (versión simplificada)
        """
        return f"""
Analiza este producto de Amazon y genera keywords optimizados en español:

PRODUCTO:
- Título: {product_input.product_name}
- Descripción: {product_input.value_proposition}
- Categoría: {product_input.category}
- Cliente objetivo: {product_input.target_customer_description}
- Keywords iniciales: {', '.join(product_input.target_keywords) if product_input.target_keywords else 'Ninguno'}

GENERA EXACTAMENTE ESTE FORMATO JSON (sin explicaciones adicionales):

{{
    "seo_strategy": {{
        "primary_keywords": ["3-5 keywords principales con alto volumen de búsqueda"],
        "secondary_keywords": ["5-8 keywords complementarias"],
        "long_tail_keywords": ["5-7 keywords de cola larga específicas"],
        "branded_keywords": ["keywords de marca si aplican"],
        "competitor_keywords": ["keywords que usan competidores"],
        "benefit_keywords": ["keywords basadas en beneficios"],
        "feature_keywords": ["keywords basadas en características"],
        "use_case_keywords": ["keywords basadas en situaciones de uso"]
    }},
    "search_terms_optimization": {{
        "frontend_terms": ["términos para título, bullets y descripción"],
        "backend_terms": ["términos para campos de búsqueda backend"],
        "seasonal_terms": ["términos estacionales relevantes"],
        "category_specific_terms": ["términos específicos de la categoría"],
        "audience_terms": ["términos específicos del público objetivo"],
        "problem_solving_terms": ["keywords que resuelven problemas"]
    }},
    "keyword_analysis": {{
        "volume_score": "8",
        "competition_level": "medio",
        "relevance_score": "9",
        "conversion_potential": "alto",
        "priority_ranking": ["lista ordenada de keywords por prioridad"]
    }},
    "implementation_strategy": {{
        "title_keywords": ["keywords prioritarias para el título"],
        "bullet_keywords": ["keywords para bullet points"],
        "description_keywords": ["keywords para descripción"],
        "backend_keywords": ["keywords para campos ocultos"],
        "ppc_keywords": ["keywords para campañas PPC"]
    }},
    "visual_assets_analysis": {{
        "available_assets": ["análisis de assets disponibles"],
        "asset_quality_assessment": "evaluación de calidad",
        "missing_visual_content": ["contenido visual faltante"],
        "visual_hierarchy_recommendation": "recomendación de jerarquía visual"
    }},
    "image_strategy": {{
        "main_image_recommendations": "recomendaciones para imagen principal",
        "secondary_images_plan": [
            {{"slot": "Imagen 2", "purpose": "mostrar características", "content_type": "infografía"}},
            {{"slot": "Imagen 3", "purpose": "demostrar beneficios", "content_type": "lifestyle"}}
        ],
        "lifestyle_photography": "estrategia de fotografía lifestyle",
        "infographic_needs": ["necesidades de infografías"]
    }},
    "a_plus_content_strategy": {{
        "content_modules": ["módulos de contenido A+ optimizados"],
        "visual_storytelling": "estrategia de storytelling visual",
        "comparison_charts": "recomendaciones para charts comparativos",
        "lifestyle_integration": "integración de imágenes lifestyle"
    }},
    "seo_bullets": [
        "Bullet optimizado con keywords principales",
        "Bullet con términos de búsqueda específicos",
        "Bullet con keywords de cola larga",
        "Bullet con términos de beneficio clave",
        "Bullet con diferenciadores SEO"
    ],
    "optimization_timeline": {{
        "immediate_actions": ["optimizar título y descripción", "implementar keywords en bullets"],
        "30_day_optimizations": ["análisis de rendimiento", "optimización basada en datos"],
        "long_term_strategy": ["expansión de keywords", "optimización competitiva continua"]
    }},
    "performance_tracking": {{
        "keywords_to_monitor": ["keywords principales para trackear"],
        "ranking_targets": "objetivos de posicionamiento",
        "conversion_metrics": ["CTR por keyword", "conversión por término", "posición orgánica"]
    }},
    "recommendations": [
        "implementación específica de keywords",
        "tests A/B de títulos",
        "estrategias para mejorar ranking",
        "próximos pasos de optimización"
    ]
}}

IMPORTANTE: Genera keywords específicos para el mercado hispanohablante, enfócate en términos que los usuarios realmente buscan en Amazon en español.
"""
    
    def _calculate_seo_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza del análisis SEO y visual
        """
        confidence = 0.0
        
        # Verificar estrategia SEO
        seo = data.get("seo_strategy", {})
        if seo.get("primary_keywords") and len(seo.get("primary_keywords", [])) >= 3:
            confidence += 0.2
        if seo.get("secondary_keywords") and len(seo.get("secondary_keywords", [])) >= 5:
            confidence += 0.15
        if seo.get("long_tail_keywords") and len(seo.get("long_tail_keywords", [])) >= 3:
            confidence += 0.1
        
        # Verificar optimización de términos de búsqueda
        search_terms = data.get("search_terms_optimization", {})
        if search_terms.get("frontend_terms") and len(search_terms.get("frontend_terms", [])) >= 5:
            confidence += 0.15
        if search_terms.get("backend_terms") and len(search_terms.get("backend_terms", [])) >= 10:
            confidence += 0.1
        
        # Verificar estrategia de imágenes
        image_strategy = data.get("image_strategy", {})
        if image_strategy.get("main_image_recommendations"):
            confidence += 0.1
        if image_strategy.get("secondary_images_plan") and len(image_strategy.get("secondary_images_plan", [])) >= 3:
            confidence += 0.1
        
        # Verificar contenido A+
        aplus = data.get("a_plus_content_strategy", {})
        if aplus.get("content_modules") and len(aplus.get("content_modules", [])) >= 2:
            confidence += 0.05
        
        # Verificar timeline de optimización
        timeline = data.get("optimization_timeline", {})
        if timeline.get("immediate_actions") and len(timeline.get("immediate_actions", [])) >= 2:
            confidence += 0.05
        
        return min(confidence, 1.0)
