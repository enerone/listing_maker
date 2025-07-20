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
        Construye el prompt especializado para SEO y visual
        """
        return f"""
Tu rol es el de un Agente de Extracción y Optimización de Keywords especializado en listings para Amazon. Realizarás dos tareas fundamentales:

FASE 1 - EXTRACCIÓN INICIAL DE KEYWORDS:

INFORMACIÓN DEL PRODUCTO:
- Título: {product_input.product_name}
- Descripción: {product_input.value_proposition}
- Categoría: {product_input.category}
- Marca: {getattr(product_input, 'brand', 'No especificada')}
- Keywords iniciales: {', '.join(product_input.target_keywords) if product_input.target_keywords else 'No especificadas'}
- Cliente objetivo: {product_input.target_customer_description}
- Situaciones de uso: {', '.join(product_input.use_situations)}
- Ventajas competitivas: {', '.join(product_input.competitive_advantages)}

INSTRUCCIONES ESPECÍFICAS:
1. Analiza cuidadosamente el título y descripción del producto
2. Extrae las keywords más relevantes que describan claramente el producto
3. Prioriza keywords con mayor volumen de búsqueda y pertinencia al producto en Amazon
4. Considera el comportamiento de búsqueda de usuarios hispanohablantes en Amazon
5. Incluye variaciones semánticas y sinónimos relevantes
6. Considera términos de búsqueda por beneficios, características y casos de uso
7. Incluye keywords de cola larga específicas para menor competencia

FASE 2 - OPTIMIZACIÓN ESTRATÉGICA:
Genera una estrategia completa de keywords optimizada considerando:
- Relevancia al producto y categoría
- Volumen de búsqueda estimado en Amazon
- Intención del usuario (informacional, transaccional, navegacional)
- Competitividad en Amazon
- Estacionalidad y tendencias
- Keywords de marca y genéricas
- Términos específicos de la categoría

FORMATO DE RESPUESTA (JSON):
{{
    "seo_strategy": {{
        "primary_keywords": ["3-5 keywords principales de alto volumen y relevancia máxima"],
        "secondary_keywords": ["5-8 keywords secundarias complementarias"],
        "long_tail_keywords": ["5-7 keywords de cola larga específicas y menos competitivas"],
        "branded_keywords": ["Keywords de marca si aplican"],
        "competitor_keywords": ["Keywords que usan competidores principales"],
        "benefit_keywords": ["Keywords basadas en beneficios del producto"],
        "feature_keywords": ["Keywords basadas en características técnicas"],
        "use_case_keywords": ["Keywords basadas en situaciones de uso"]
    }},
    "search_terms_optimization": {{
        "frontend_terms": ["Términos optimizados para título, bullets y descripción"],
        "backend_terms": ["Términos para campos de búsqueda backend de Amazon"],
        "seasonal_terms": ["Términos estacionales relevantes"],
        "category_specific_terms": ["Términos específicos de la categoría del producto"],
        "audience_terms": ["Términos específicos del público objetivo"],
        "problem_solving_terms": ["Keywords que resuelven problemas del cliente"]
    }},
    "keyword_analysis": {{
        "volume_score": "Puntuación estimada de volumen de búsqueda (1-10)",
        "competition_level": "Nivel de competencia estimado (bajo/medio/alto)",
        "relevance_score": "Puntuación de relevancia al producto (1-10)",
        "conversion_potential": "Potencial de conversión estimado (bajo/medio/alto)",
        "priority_ranking": ["Lista ordenada de keywords por prioridad de implementación"]
    }},
    "implementation_strategy": {{
        "title_keywords": ["Keywords prioritarias para incluir en el título"],
        "bullet_keywords": ["Keywords para distribuir en bullet points"],
        "description_keywords": ["Keywords para descripción principal"],
        "backend_keywords": ["Keywords para campos ocultos de Amazon"],
        "ppc_keywords": ["Keywords recomendadas para campañas PPC"]
    }},
    "visual_assets_analysis": {{
        "available_assets": {product_input.available_assets if product_input.available_assets else ["No especificados"]},
        "asset_quality_assessment": "Evaluación de calidad de los assets existentes",
        "missing_visual_content": ["Contenido visual faltante crítico basado en keywords"],
        "visual_hierarchy_recommendation": "Recomendación de jerarquía visual basada en keywords principales"
    }},
    "image_strategy": {{
        "main_image_recommendations": "Recomendaciones para imagen principal optimizada para keywords",
        "secondary_images_plan": [
            {{
                "slot": "Imagen 2",
                "purpose": "Mostrar características clave basadas en keywords",
                "content_type": "Tipo de contenido que refuerce keywords principales"
            }},
            {{
                "slot": "Imagen 3", 
                "purpose": "Demostrar beneficios basados en keywords de beneficios",
                "content_type": "Contenido que conecte con términos de búsqueda emocionales"
            }}
        ],
        "lifestyle_photography": "Estrategia de fotografía lifestyle que refuerce keywords de uso",
        "infographic_needs": ["Necesidades de infografías basadas en keywords técnicas"]
    }},
    "a_plus_content_strategy": {{
        "content_modules": ["Módulos de contenido A+ optimizados para keywords"],
        "visual_storytelling": "Estrategia de storytelling visual que incorpore keywords naturalmente",
        "comparison_charts": "Recomendaciones para charts comparativos con keywords competitivas",
        "lifestyle_integration": "Integración de imágenes lifestyle con keywords de uso"
    }},
    "seo_bullets": [
        "🔍 Bullet optimizado con keywords principales: [ejemplo específico]",
        "📊 Bullet con términos de búsqueda específicos: [ejemplo específico]", 
        "🎯 Bullet con keywords de cola larga: [ejemplo específico]",
        "⭐ Bullet con términos de beneficio clave: [ejemplo específico]",
        "🏆 Bullet con diferenciadores SEO: [ejemplo específico]"
    ],
    "optimization_timeline": {{
        "immediate_actions": ["Optimizar título y descripción con keywords principales", "Implementar keywords en bullets"],
        "30_day_optimizations": ["Análisis de rendimiento de keywords", "Optimización basada en datos"],
        "long_term_strategy": ["Expansión de keywords basada en estacionalidad", "Optimización competitiva continua"]
    }},
    "performance_tracking": {{
        "keywords_to_monitor": ["Keywords principales para trackear ranking"],
        "ranking_targets": "Objetivos de posicionamiento para keywords prioritarias",
        "conversion_metrics": ["CTR por keyword", "Conversión por término de búsqueda", "Posición orgánica promedio"]
    }},
    "recommendations": [
        "Recomendaciones específicas de implementación de keywords",
        "Sugerencias para tests A/B de títulos con diferentes keywords",
        "Estrategias para mejorar ranking orgánico",
        "Próximos pasos para optimización continua"
    ]
}

CRITERIOS DE CALIDAD:
- Todas las keywords deben ser específicamente relevantes para el mercado hispanohablante
- Prioriza términos que los clientes realmente buscan en Amazon México/España
- Incluye variaciones gramaticales y errores de escritura comunes
- Considera diferencias regionales en terminología
- Equilibra keywords de alta y baja competencia
- Asegura que las keywords sean naturales y no afecten la legibilidad

IMPORTANTE: Organiza todas las keywords por orden de importancia y relevancia para facilitar su uso posterior en títulos, descripciones y campañas publicitarias.
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
- Competitividad en Amazon
- Estacionalidad y tendencias
- Keywords de marca y genéricas
- Términos específicos de la categoría

FORMATO DE RESPUESTA (JSON):
{{
    "seo_strategy": {{
        "primary_keywords": ["3-5 keywords principales de alto volumen y relevancia máxima"],
        "secondary_keywords": ["5-8 keywords secundarias complementarias"],
        "long_tail_keywords": ["5-7 keywords de cola larga específicas y menos competitivas"],
        "branded_keywords": ["Keywords de marca si aplican"],
        "competitor_keywords": ["Keywords que usan competidores principales"],
        "benefit_keywords": ["Keywords basadas en beneficios del producto"],
        "feature_keywords": ["Keywords basadas en características técnicas"],
        "use_case_keywords": ["Keywords basadas en situaciones de uso"]
    }},
    "search_terms_optimization": {{
        "frontend_terms": ["Términos optimizados para título, bullets y descripción"],
        "backend_terms": ["Términos para campos de búsqueda backend de Amazon"],
        "seasonal_terms": ["Términos estacionales relevantes"],
        "category_specific_terms": ["Términos específicos de la categoría del producto"],
        "audience_terms": ["Términos específicos del público objetivo"],
        "problem_solving_terms": ["Keywords que resuelven problemas del cliente"]
    }},
    "keyword_analysis": {{
        "volume_score": "Puntuación estimada de volumen de búsqueda (1-10)",
        "competition_level": "Nivel de competencia estimado (bajo/medio/alto)",
        "relevance_score": "Puntuación de relevancia al producto (1-10)",
        "conversion_potential": "Potencial de conversión estimado (bajo/medio/alto)",
        "priority_ranking": ["Lista ordenada de keywords por prioridad de implementación"]
    }},
    "implementation_strategy": {{
        "title_keywords": ["Keywords prioritarias para incluir en el título"],
        "bullet_keywords": ["Keywords para distribuir en bullet points"],
        "description_keywords": ["Keywords para descripción principal"],
        "backend_keywords": ["Keywords para campos ocultos de Amazon"],
        "ppc_keywords": ["Keywords recomendadas para campañas PPC"]
    }},
    "visual_assets_analysis": {{
        "available_assets": {product_input.available_assets if product_input.available_assets else ["No especificados"]},
        "asset_quality_assessment": "Evaluación de calidad de los assets existentes",
        "missing_visual_content": ["Contenido visual faltante crítico basado en keywords"],
        "visual_hierarchy_recommendation": "Recomendación de jerarquía visual basada en keywords principales"
    }},
    "image_strategy": {{
        "main_image_recommendations": "Recomendaciones para imagen principal optimizada para keywords",
        "secondary_images_plan": [
            {{
                "slot": "Imagen 2",
                "purpose": "Mostrar características clave basadas en keywords",
                "content_type": "Tipo de contenido que refuerce keywords principales"
            }},
            {{
                "slot": "Imagen 3", 
                "purpose": "Demostrar beneficios basados en keywords de beneficios",
                "content_type": "Contenido que conecte con términos de búsqueda emocionales"
            }}
        ],
        "lifestyle_photography": "Estrategia de fotografía lifestyle que refuerce keywords de uso",
        "infographic_needs": ["Necesidades de infografías basadas en keywords técnicas"]
    }},
    "a_plus_content_strategy": {{
        "content_modules": ["Módulos de contenido A+ optimizados para keywords"],
        "visual_storytelling": "Estrategia de storytelling visual que incorpore keywords naturalmente",
        "comparison_charts": "Recomendaciones para charts comparativos con keywords competitivas",
        "lifestyle_integration": "Integración de imágenes lifestyle con keywords de uso"
    }},
    "seo_bullets": [
        "🔍 Bullet optimizado con keywords principales: [ejemplo específico]",
        "📊 Bullet con términos de búsqueda específicos: [ejemplo específico]", 
        "🎯 Bullet con keywords de cola larga: [ejemplo específico]",
        "⭐ Bullet con términos de beneficio clave: [ejemplo específico]",
        "🏆 Bullet con diferenciadores SEO: [ejemplo específico]"
    ],
    "optimization_timeline": {{
        "immediate_actions": ["Optimizar título y descripción con keywords principales", "Implementar keywords en bullets"],
        "30_day_optimizations": ["Análisis de rendimiento de keywords", "Optimización basada en datos"],
        "long_term_strategy": ["Expansión de keywords basada en estacionalidad", "Optimización competitiva continua"]
    }},
    "performance_tracking": {{
        "keywords_to_monitor": ["Keywords principales para trackear ranking"],
        "ranking_targets": "Objetivos de posicionamiento para keywords prioritarias",
        "conversion_metrics": ["CTR por keyword", "Conversión por término de búsqueda", "Posición orgánica promedio"]
    }},
    "recommendations": [
        "Recomendaciones específicas de implementación de keywords",
        "Sugerencias para tests A/B de títulos con diferentes keywords",
        "Estrategias para mejorar ranking orgánico",
        "Próximos pasos para optimización continua"
    ]
}}

CRITERIOS DE CALIDAD:
- Todas las keywords deben ser específicamente relevantes para el mercado hispanohablante
- Prioriza términos que los clientes realmente buscan en Amazon México/España
- Incluye variaciones gramaticales y errores de escritura comunes
- Considera diferencias regionales en terminología
- Equilibra keywords de alta y baja competencia
- Asegura que las keywords sean naturales y no afecten la legibilidad
- Máximo 30 keywords en total, organizadas por importancia y relevancia

IMPORTANTE: Organiza todas las keywords por orden de importancia y relevancia para facilitar su uso posterior en títulos, descripciones y campañas publicitarias.
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
