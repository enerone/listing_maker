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
Eres estratégico, orientado a resultados y entiendes el comportamiento del comprador online."""
    
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
            parsed_response = await self._generate_response(prompt, structured=True)
            
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
        Construye el prompt especializado para SEO y visual
        """
        return f"""
Eres un experto en SEO para Amazon y optimización visual. Analiza la siguiente información del producto y desarrolla una estrategia completa de SEO y contenido visual.

INFORMACIÓN DEL PRODUCTO:
Nombre: {product_input.product_name}
Categoría: {product_input.category}
Precio objetivo: ${product_input.target_price}
Keywords objetivo: {', '.join(product_input.target_keywords)}
Cliente objetivo: {product_input.target_customer_description}
Situaciones de uso: {', '.join(product_input.use_situations)}
Propuesta de valor: {product_input.value_proposition}
Ventajas competitivas: {', '.join(product_input.competitive_advantages)}
Assets disponibles: {', '.join(product_input.available_assets) if product_input.available_assets else 'No especificados'}
Descripción de assets: {', '.join(product_input.asset_descriptions) if product_input.asset_descriptions else 'No especificada'}

TAREA:
Desarrolla una estrategia completa de SEO y contenido visual que incluya:

1. **Optimización de keywords** para Amazon A9
2. **Estrategia de términos de búsqueda** backend y frontend
3. **Análisis de activos visuales** disponibles
4. **Recomendaciones de contenido visual** para maximizar conversión
5. **Plan de optimización SEO** a corto y largo plazo

FORMATO DE RESPUESTA (JSON):
{{
    "seo_strategy": {{
        "primary_keywords": ["Keywords", "principales", "de", "alto", "volumen"],
        "secondary_keywords": ["Keywords", "secundarias", "complementarias"],
        "long_tail_keywords": ["Keywords", "de", "cola", "larga", "específicas"],
        "branded_keywords": ["Keywords", "de", "marca", "si", "aplican"],
        "competitor_keywords": ["Keywords", "de", "competencia", "identificadas"]
    }},
    "search_terms_optimization": {{
        "frontend_terms": ["Términos", "visibles", "en", "título", "y", "bullets"],
        "backend_terms": ["Términos", "para", "campos", "de", "búsqueda", "backend"],
        "seasonal_terms": ["Términos", "estacionales", "relevantes"],
        "category_specific_terms": ["Términos", "específicos", "de", "la", "categoría"]
    }},
    "visual_assets_analysis": {{
        "available_assets": ["Lista", "de", "assets", "disponibles", "analizados"],
        "asset_quality_assessment": "Evaluación de calidad de los assets existentes",
        "missing_visual_content": ["Contenido", "visual", "faltante", "crítico"],
        "visual_hierarchy_recommendation": "Recomendación de jerarquía visual"
    }},
    "image_strategy": {{
        "main_image_recommendations": "Recomendaciones para imagen principal",
        "secondary_images_plan": [
            {{
                "slot": "Imagen 2",
                "purpose": "Propósito de la imagen",
                "content_type": "Tipo de contenido recomendado"
            }}
        ],
        "lifestyle_photography": "Estrategia de fotografía lifestyle",
        "infographic_needs": ["Necesidades", "de", "infografías", "específicas"]
    }},
    "a_plus_content_strategy": {{
        "content_modules": ["Módulos", "de", "contenido", "A+", "recomendados"],
        "visual_storytelling": "Estrategia de storytelling visual",
        "comparison_charts": "Recomendaciones para charts comparativos",
        "lifestyle_integration": "Integración de imágenes lifestyle"
    }},
    "seo_bullets": [
        "🔍 Bullet optimizado con keywords principales",
        "📊 Bullet con términos de búsqueda específicos",
        "🎯 Bullet con keywords de cola larga",
        "⭐ Bullet con términos de beneficio clave",
        "🏆 Bullet con diferenciadores SEO"
    ],
    "optimization_timeline": {{
        "immediate_actions": ["Acciones", "inmediatas", "de", "SEO"],
        "30_day_optimizations": ["Optimizaciones", "a", "30", "días"],
        "long_term_strategy": ["Estrategia", "a", "largo", "plazo"]
    }},
    "performance_tracking": {{
        "keywords_to_monitor": ["Keywords", "clave", "para", "monitorear"],
        "ranking_targets": "Objetivos de ranking específicos",
        "conversion_metrics": ["Métricas", "de", "conversión", "a", "trackear"]
    }},
    "recommendations": [
        "Recomendaciones específicas para mejorar SEO",
        "Sugerencias para optimizar contenido visual",
        "Próximos pasos para implementar la estrategia"
    ]
}}

INSTRUCCIONES IMPORTANTES:
- Usa las keywords objetivo proporcionadas como base, pero expándelas estratégicamente
- Considera la categoría del producto para keywords específicas del nicho
- Las recomendaciones visuales deben ser específicas y prácticas
- Incluye términos que los clientes realmente buscan en Amazon
- Prioriza keywords con potencial de conversión alta
- Las recomendaciones deben ser implementables con el presupuesto típico de un seller
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
