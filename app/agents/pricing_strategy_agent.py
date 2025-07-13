from typing import Dict, Any
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class PricingStrategyAgent(BaseAgent):
    """
    Agente especializado en desarrollar estrategia de precios y promociones.
    
    Responsabilidades:
    - Analizar precio objetivo en contexto de mercado
    - Desarrollar estrategia de pricing competitiva
    - Sugerir estructura de promociones
    - Optimizar precio para conversión en Amazon
    """
    
    def __init__(self, temperature: float = 0.5):
        super().__init__(
            agent_name="Pricing Strategy Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de estrategia de precios
        """
        return """Eres un experto en estrategia de precios para Amazon y e-commerce. 
Tu trabajo es desarrollar estrategias de precios que maximicen conversión y rentabilidad.
Entiendes la psicología de precios, competencia y posicionamiento en marketplace.
Siempre devuelves respuestas en formato JSON válido.
Eres estratégico, analítico y orientado a resultados comerciales."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Desarrolla estrategia de precios para el producto
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análisis de pricing para: {product_input.product_name}")
            
            # Preparar prompt especializado para pricing
            prompt = self._build_pricing_prompt(product_input)
            
            # Generar respuesta con Ollama
            parsed_response = await self._generate_response(prompt, structured=True)
            
            processing_time = time.time() - start_time
            
            # Crear respuesta del agente
            response = AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data=parsed_response,
                confidence=self._calculate_pricing_confidence(parsed_response),
                processing_time=processing_time,
                notes=[
                    "Estrategia de precios desarrollada",
                    "Análisis competitivo de precios realizado",
                    "Estructura de promociones sugerida",
                    "Optimización para Amazon marketplace"
                ],
                recommendations=parsed_response.get("recommendations", [])
            )
            
            logger.info(f"Análisis de pricing completado con confianza: {response.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error en análisis de pricing: {str(e)}")
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                data={},
                confidence=0.0,
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"]
            )
    
    def _build_pricing_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt especializado para estrategia de precios
        """
        return f"""
Eres un experto en estrategia de precios para Amazon. Analiza la siguiente información del producto y desarrolla una estrategia de precios completa y competitiva.

INFORMACIÓN DEL PRODUCTO:
Nombre: {product_input.product_name}
Categoría: {product_input.category}
Precio objetivo: ${product_input.target_price}
Propuesta de valor: {product_input.value_proposition}
Ventajas competitivas: {', '.join(product_input.competitive_advantages)}
Notas de estrategia de precios: {product_input.pricing_strategy_notes}
Cliente objetivo: {product_input.target_customer_description}
Situaciones de uso: {', '.join(product_input.use_situations)}

TAREA:
Desarrolla una estrategia de precios completa que incluya:

1. **Análisis del precio objetivo** en contexto de mercado
2. **Posicionamiento de precio** vs competencia
3. **Estrategia de lanzamiento** y promociones
4. **Optimización para conversión** en Amazon
5. **Estructura de descuentos** y ofertas

FORMATO DE RESPUESTA (JSON):
{{
    "price_analysis": {{
        "target_price": {product_input.target_price},
        "price_positioning": "Premium/Mid-range/Budget con justificación",
        "value_per_dollar": "Análisis de valor por dólar gastado",
        "price_psychology": "Aspectos psicológicos del precio elegido"
    }},
    "competitive_strategy": {{
        "estimated_competitor_range": {{
            "low": "Precio estimado más bajo en la categoría",
            "high": "Precio estimado más alto en la categoría",
            "average": "Precio promedio estimado del mercado"
        }},
        "competitive_positioning": "Cómo se posiciona vs competencia",
        "differentiation_factors": ["Factores", "que", "justifican", "el", "precio"]
    }},
    "launch_strategy": {{
        "initial_price": "Precio de lanzamiento recomendado",
        "promotional_phases": [
            {{
                "phase": "Lanzamiento",
                "duration": "Duración de la fase",
                "price_strategy": "Estrategia específica",
                "discount_percentage": "Porcentaje de descuento si aplica"
            }}
        ],
        "price_optimization_timeline": "Plan de optimización de precios"
    }},
    "promotion_structure": {{
        "early_bird_discount": {{
            "percentage": "Porcentaje de descuento",
            "duration": "Duración del descuento",
            "conditions": "Condiciones del descuento"
        }},
        "bundle_opportunities": ["Oportunidades", "de", "bundles"],
        "seasonal_pricing": "Estrategia de precios estacionales",
        "volume_discounts": "Estructura de descuentos por volumen"
    }},
    "amazon_optimization": {{
        "buy_box_strategy": "Estrategia para ganar Buy Box",
        "pricing_automation": "Recomendaciones de automatización",
        "competitor_monitoring": "Estrategia de monitoreo de competencia",
        "dynamic_pricing_rules": ["Reglas", "de", "pricing", "dinámico"]
    }},
    "pricing_bullets": [
        "💰 Bullet destacando el valor del precio",
        "🎯 Bullet sobre positioning vs competencia",
        "🎁 Bullet sobre ofertas especiales",
        "📈 Bullet sobre valor a largo plazo",
        "✨ Bullet sobre propuesta de valor única"
    ],
    "recommendations": [
        "Recomendaciones para optimizar la estrategia de precios",
        "Ajustes sugeridos basados en el análisis",
        "Próximos pasos para implementar la estrategia"
    ]
}}

INSTRUCCIONES IMPORTANTES:
- Basa el análisis en la información real proporcionada
- Considera la categoría del producto para el análisis competitivo
- La estrategia debe ser práctica e implementable en Amazon
- Incluye consideraciones de psicología de precios
- Sugiere precios específicos y rangos realistas para la categoría
"""
    
    def _calculate_pricing_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza del análisis de pricing
        """
        confidence = 0.0
        
        # Verificar análisis de precio
        price_analysis = data.get("price_analysis", {})
        if price_analysis.get("price_positioning"):
            confidence += 0.2
        if price_analysis.get("value_per_dollar"):
            confidence += 0.15
        
        # Verificar estrategia competitiva
        competitive = data.get("competitive_strategy", {})
        if competitive.get("competitive_positioning"):
            confidence += 0.15
        competitor_range = competitive.get("estimated_competitor_range", {})
        if competitor_range.get("low") and competitor_range.get("high"):
            confidence += 0.1
        
        # Verificar estrategia de lanzamiento
        launch = data.get("launch_strategy", {})
        if launch.get("initial_price"):
            confidence += 0.15
        if launch.get("promotional_phases") and len(launch.get("promotional_phases", [])) > 0:
            confidence += 0.1
        
        # Verificar estructura de promociones
        promotion = data.get("promotion_structure", {})
        if promotion.get("early_bird_discount"):
            confidence += 0.1
        
        # Verificar optimización para Amazon
        amazon_opt = data.get("amazon_optimization", {})
        if amazon_opt.get("buy_box_strategy"):
            confidence += 0.05
        
        return min(confidence, 1.0)
