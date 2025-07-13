from typing import Dict, Any
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class CompetitiveAnalysisAgent(BaseAgent):
    """
    Agente especializado en análisis competitivo profundo.
    
    Responsabilidades:
    - Identificar competidores directos e indirectos
    - Analizar estrategias de precios competitivas
    - Evaluar fortalezas y debilidades vs competencia
    - Generar estrategias de diferenciación
    - Proponer posicionamiento competitivo
    """
    
    def __init__(self, temperature: float = 0.4):
        super().__init__(
            agent_name="Competitive Analysis Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de análisis competitivo
        """
        return """Eres un experto en análisis competitivo para Amazon.
Responde ÚNICAMENTE con JSON válido:

{
    "competitors": ["Competidor 1", "Competidor 2"],
    "competitive_advantages": [
        {
            "advantage": "Ventaja clave",
            "strength": "high",
            "impact": "Descripción del impacto"
        }
    ],
    "market_positioning": "Posición en el mercado",
    "pricing_strategy": "Estrategia de precios",
    "differentiation_points": ["Punto 1", "Punto 2"],
    "confidence_score": 0.9,
    "recommendations": ["Recomendación 1"]
}"""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Realiza análisis competitivo completo del producto
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análisis competitivo para: {product_input.product_name}")
            
            # Preparar prompt especializado para análisis competitivo
            prompt = self._build_competitive_prompt(product_input)
            
            # Generar respuesta con Ollama
            parsed_response = await self._generate_response(prompt, structured=True)
            
            processing_time = time.time() - start_time
            
            # Crear respuesta del agente
            response = AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data=parsed_response,
                confidence=self._calculate_competitive_confidence(parsed_response),
                processing_time=processing_time,
                notes=[
                    "Competidores principales identificados",
                    "Análisis de gaps competitivos realizado",
                    "Estrategia de diferenciación desarrollada",
                    "Posicionamiento competitivo definido"
                ],
                recommendations=parsed_response.get("recommendations", [])
            )
            
            logger.info(f"Análisis competitivo completado con confianza: {response.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error en análisis competitivo: {str(e)}")
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                data={},
                confidence=0.0,
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"]
            )
    
    def _build_competitive_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt especializado para análisis competitivo
        """
        return f"""
Analiza la competencia para: {product_input.product_name}
Categoría: {product_input.category}
Precio: ${product_input.target_price}
Target: {product_input.target_customer_description}

Identifica 3 competidores principales y ventajas competitivas clave.
Responde SOLO con JSON según el formato del prompt del sistema.
"""
                "significance": "Alto/Medio/Bajo",
                "sustainability": "Qué tan sostenible es esta ventaja"
            }}
        ],
        "our_disadvantages": [
            {{
                "disadvantage": "Desventaja identificada",
                "impact": "Nivel de impacto",
                "mitigation_strategy": "Cómo mitigar esta desventaja"
            }}
        ],
        "market_gaps": [
            {{
                "gap": "Gap del mercado identificado",
                "opportunity_size": "Tamaño de la oportunidad",
                "difficulty_to_capture": "Dificultad para capturar"
            }}
        ]
    }},
    "pricing_strategy": {{
        "competitive_pricing_analysis": {{
            "market_price_range": "$XX - $XX",
            "sweet_spot_price": "$XX",
            "premium_justification": "Por qué podemos cobrar premium",
            "discount_threats": "Amenazas de guerra de precios"
        }},
        "pricing_recommendations": {{
            "launch_price": "$XX",
            "pricing_rationale": "Razón estratégica del precio",
            "promotional_strategy": "Estrategia promocional vs competencia",
            "long_term_pricing": "Estrategia de precios a largo plazo"
        }}
    }},
    "differentiation_strategy": {{
        "unique_value_proposition": "Propuesta de valor única vs competencia",
        "key_differentiators": [
            {{
                "differentiator": "Factor diferenciador",
                "customer_impact": "Impacto en el cliente",
                "competitive_moat": "Qué tan difícil de copiar es"
            }}
        ],
        "messaging_strategy": {{
            "primary_message": "Mensaje principal vs competencia",
            "proof_points": ["Puntos de prueba de superioridad"],
            "customer_testimonial_focus": "En qué enfocar testimoniales"
        }}
    }},
    "positioning_strategy": {{
        "market_position": "Posición deseada en el mercado",
        "target_customer_segment": "Segmento específico a targetear",
        "brand_personality": "Personalidad de marca vs competencia",
        "communication_tone": "Tono de comunicación diferenciado"
    }},
    "competitive_keywords": {{
        "competitor_keywords_to_target": ["Keywords que usan competidores exitosos"],
        "underserved_keywords": ["Keywords con poca competencia"],
        "branded_keywords_defense": ["Keywords de marca a defender"],
        "keyword_gaps": ["Gaps de keywords vs competencia"]
    }},
    "action_plan": {{
        "immediate_actions": [
            "Acciones inmediatas para ganar ventaja competitiva"
        ],
        "30_day_strategy": [
            "Estrategias a implementar en 30 días"
        ],
        "long_term_competitive_moat": [
            "Cómo construir ventajas competitivas sostenibles"
        ]
    }},
    "recommendations": [
        "Recomendaciones específicas para superar a la competencia",
        "Tácticas para capturar market share",
        "Estrategias de defensa contra nuevos entrantes"
    ]
}}

INSTRUCCIONES IMPORTANTES:
- Sé específico en el análisis de competidores reales de esta categoría
- Considera tanto competencia directa como indirecta
- Las recomendaciones de precios deben ser realistas y basadas en valor
- Identifica oportunidades reales de diferenciación
- Propón estrategias implementables con recursos limitados
- Enfócate en ventajas competitivas sostenibles a largo plazo
"""
    
    def _calculate_competitive_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza del análisis competitivo
        """
        confidence = 0.0
        
        # Verificar análisis de competidores
        landscape = data.get("competitive_landscape", {})
        if landscape.get("direct_competitors") and len(landscape.get("direct_competitors", [])) >= 2:
            confidence += 0.25
        
        # Verificar análisis competitivo
        analysis = data.get("competitive_analysis", {})
        if analysis.get("our_advantages") and len(analysis.get("our_advantages", [])) >= 2:
            confidence += 0.2
        
        # Verificar estrategia de diferenciación
        diff_strategy = data.get("differentiation_strategy", {})
        if diff_strategy.get("unique_value_proposition"):
            confidence += 0.2
        
        # Verificar estrategia de precios
        pricing = data.get("pricing_strategy", {})
        if pricing.get("pricing_recommendations", {}).get("launch_price"):
            confidence += 0.15
        
        # Verificar plan de acción
        action_plan = data.get("action_plan", {})
        if action_plan.get("immediate_actions") and len(action_plan.get("immediate_actions", [])) >= 3:
            confidence += 0.2
        
        return min(confidence, 1.0)
