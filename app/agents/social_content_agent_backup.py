from typing import Dict, Any
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class SocialContentAgent(BaseAgent):
    """
    Agente especializado en generación de hashtags y contenido social.
    
    Responsabilidades:
    - Generar hashtags estratégicos para múltiples plataformas
    - Crear contenido social optimizado
    - Desarrollar calendario de contenido
    - Proponer campañas de influencers
    - Generar copy para diferentes audiencias
    """
    
    def __init__(self, temperature: float = 0.6):
        super().__init__(
            agent_name="Social Content Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de contenido social
        """
        return """Eres un experto en marketing de contenido y estrategia social media. 
Tu trabajo es crear contenido viral, hashtags estratégicos y campañas que generen engagement.
Entiendes las dinámicas de cada plataforma social y cómo maximizar reach y conversión.
Siempre devuelves respuestas en formato JSON válido.
Eres creativo, estratégico y orientado a generar buzz y ventas."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Genera estrategia completa de contenido social y hashtags
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando generación de contenido social para: {product_input.product_name}")
            
            # Preparar prompt especializado para contenido social
            prompt = self._build_social_content_prompt(product_input)
            
            # Generar respuesta con Ollama
            parsed_response = await self._generate_response(prompt, structured=True)
            
            processing_time = time.time() - start_time
            
            # Crear respuesta del agente
            response = AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data=parsed_response,
                confidence=self._calculate_social_confidence(parsed_response),
                processing_time=processing_time,
                notes=[
                    "Hashtags estratégicos generados",
                    "Contenido social optimizado creado",
                    "Estrategia de influencers desarrollada",
                    "Calendario de contenido propuesto"
                ],
                recommendations=parsed_response.get("recommendations", [])
            )
            
            logger.info(f"Contenido social generado con confianza: {response.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error en generación de contenido social: {str(e)}")
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                data={},
                confidence=0.0,
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"]
            )
    
    def _build_social_content_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt especializado para contenido social
        """
        return f"""
Eres un experto en marketing de contenido y social media. Crea una estrategia completa de contenido social y hashtags para el siguiente producto.

INFORMACIÓN DEL PRODUCTO:
Nombre: {product_input.product_name}
Categoría: {product_input.category}
Precio: ${product_input.target_price}
Cliente objetivo: {product_input.target_customer_description}
Situaciones de uso: {', '.join(product_input.use_situations)}
Propuesta de valor: {product_input.value_proposition}
Ventajas competitivas: {', '.join(product_input.competitive_advantages)}

TAREA:
Desarrolla una estrategia completa de contenido social que incluya:

1. **Hashtags estratégicos** para múltiples plataformas
2. **Contenido viral** y posts optimizados
3. **Estrategia de influencers** y colaboraciones
4. **Calendario de contenido** estacional
5. **Copy variations** para diferentes audiencias

FORMATO DE RESPUESTA (JSON):
{{
    "hashtag_strategy": {{
        "primary_hashtags": [
            "#HashtagPrincipal",
            "#SegundoHashtag",
            "#TercerHashtag"
        ],
        "platform_specific": {{
            "instagram": {{
                "trending_hashtags": ["#Hashtags", "#DeModa", "#EnInstagram"],
                "niche_hashtags": ["#HashtagsDeNicho", "#MuyEspecificos"],
                "community_hashtags": ["#HashtagsDeComunidad", "#ParaEngagement"]
            }},
            "tiktok": {{
                "viral_hashtags": ["#HashtagsVirales", "#EnTikTok"],
                "challenge_hashtags": ["#Challenge", "#Potencial"],
                "trend_hashtags": ["#TrendingAhora", "#Populares"]
            }},
            "facebook": {{
                "brand_hashtags": ["#HashtagsDeMarca", "#Corporativos"],
                "local_hashtags": ["#HashtagsLocales", "#Geografia"],
                "event_hashtags": ["#HashtagsDeEventos", "#Estacionales"]
            }},
            "linkedin": {{
                "professional_hashtags": ["#HashtagsProfesionales", "#B2B"],
                "industry_hashtags": ["#HashtagsDeIndustria", "#Sector"],
                "thought_leadership": ["#LiderazgoDePensamiento", "#Expertise"]
            }}
        }},
        "seasonal_hashtags": {{
            "spring": ["#Primavera", "#HashtagsPrimavera"],
            "summer": ["#Verano", "#HashtagsVerano"],
            "fall": ["#Otoño", "#HashtagsOtoño"],
            "winter": ["#Invierno", "#HashtagsInvierno"],
            "holidays": ["#NavidadHashtags", "#FeriadosEspeciales"]
        }}
    }},
    "content_strategy": {{
        "viral_content_ideas": [
            {{
                "concept": "Concepto de contenido viral",
                "platform": "Plataforma objetivo",
                "hook": "Gancho para captar atención",
                "call_to_action": "Call to action específico"
            }}
        ],
        "user_generated_content": {{
            "ugc_campaigns": [
                {{
                    "campaign_name": "Nombre de campaña UGC",
                    "hashtag": "#HashtagDeCampaña",
                    "incentive": "Incentivo para participar",
                    "content_brief": "Brief para los usuarios"
                }}
            ],
            "contest_ideas": [
                "Ideas para concursos que generen engagement"
            ]
        }},
        "educational_content": [
            {{
                "topic": "Tema educativo",
                "format": "Formato de contenido",
                "value_provided": "Valor que aporta al usuario"
            }}
        ],
        "behind_the_scenes": [
            "Ideas para contenido behind the scenes que humanice la marca"
        ]
    }},
    "influencer_strategy": {{
        "micro_influencers": {{
            "target_follower_range": "1K-100K",
            "ideal_niches": ["Nicho1", "Nicho2", "Nicho3"],
            "collaboration_types": ["Tipo de collab", "Otro tipo"],
            "budget_per_post": "$XX-$XX"
        }},
        "macro_influencers": {{
            "target_follower_range": "100K-1M",
            "ideal_profiles": ["Perfil ideal 1", "Perfil ideal 2"],
            "campaign_types": ["Tipo de campaña", "Otro tipo"],
            "expected_reach": "Reach esperado"
        }},
        "influencer_brief": {{
            "key_messages": ["Mensaje clave 1", "Mensaje clave 2"],
            "required_hashtags": ["#HashtagObligatorio", "#OtroObligatorio"],
            "content_guidelines": ["Guideline 1", "Guideline 2"],
            "deliverables": ["Post en feed", "Stories", "Reels"]
        }}
    }},
    "content_calendar": {{
        "weekly_themes": {{
            "monday": "Tema para lunes",
            "tuesday": "Tema para martes",
            "wednesday": "Tema para miércoles",
            "thursday": "Tema para jueves",
            "friday": "Tema para viernes",
            "saturday": "Tema para sábado",
            "sunday": "Tema para domingo"
        }},
        "monthly_campaigns": [
            {{
                "month": "Enero",
                "campaign_theme": "Tema de campaña",
                "key_dates": ["Fecha importante 1", "Fecha importante 2"],
                "content_focus": "Enfoque de contenido del mes"
            }}
        ],
        "seasonal_activations": [
            {{
                "season": "Temporada",
                "activation_theme": "Tema de activación",
                "duration": "Duración de la campaña",
                "expected_outcome": "Resultado esperado"
            }}
        ]
    }},
    "copy_variations": {{
        "product_announcements": [
            "Copy para anuncio de producto - Variación 1",
            "Copy para anuncio de producto - Variación 2"
        ],
        "promotional_posts": [
            "Copy promocional - Versión urgencia",
            "Copy promocional - Versión beneficio"
        ],
        "customer_testimonials": [
            "Template para testimoniales de clientes"
        ],
        "how_to_content": [
            "Copy para contenido educativo/tutorial"
        ]
    }},
    "engagement_tactics": {{
        "community_building": [
            "Táctica para construir comunidad 1",
            "Táctica para construir comunidad 2"
        ],
        "viral_triggers": [
            "Trigger viral 1: Emocional",
            "Trigger viral 2: Controversial",
            "Trigger viral 3: Trend-jacking"
        ],
        "engagement_hooks": [
            "Hook para generar comentarios",
            "Hook para generar shares",
            "Hook para generar saves"
        ]
    }},
    "performance_metrics": {{
        "kpis_to_track": [
            "Engagement rate",
            "Reach orgánico",
            "Click-through rate",
            "Conversión a ventas"
        ],
        "success_benchmarks": {{
            "engagement_rate": "X%",
            "follower_growth": "X per month",
            "ugc_generation": "X posts per week"
        }}
    }},
    "recommendations": [
        "Recomendaciones específicas para maximizar viral potential",
        "Estrategias para aumentar engagement orgánico",
        "Tácticas para convertir seguidores en clientes"
    ]
}}

INSTRUCCIONES IMPORTANTES:
- Los hashtags deben ser reales y relevantes para la audiencia objetivo
- El contenido debe ser auténtico y alineado con la marca
- Las estrategias deben ser implementables con presupuesto limitado
- Prioriza contenido que genere engagement genuino
- Considera las tendencias actuales pero mantén relevancia con el producto
- Las colaboraciones de influencers deben ser cost-effective
"""
    
    def _calculate_social_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza de la estrategia social
        """
        confidence = 0.0
        
        # Verificar estrategia de hashtags
        hashtag_strategy = data.get("hashtag_strategy", {})
        if hashtag_strategy.get("primary_hashtags") and len(hashtag_strategy.get("primary_hashtags", [])) >= 5:
            confidence += 0.2
        
        # Verificar contenido estratégico
        content_strategy = data.get("content_strategy", {})
        if content_strategy.get("viral_content_ideas") and len(content_strategy.get("viral_content_ideas", [])) >= 3:
            confidence += 0.25
        
        # Verificar estrategia de influencers
        influencer_strategy = data.get("influencer_strategy", {})
        if influencer_strategy.get("micro_influencers") and influencer_strategy.get("macro_influencers"):
            confidence += 0.2
        
        # Verificar calendario de contenido
        content_calendar = data.get("content_calendar", {})
        if content_calendar.get("weekly_themes") and content_calendar.get("monthly_campaigns"):
            confidence += 0.15
        
        # Verificar variaciones de copy
        copy_variations = data.get("copy_variations", {})
        if len(copy_variations.keys()) >= 3:
            confidence += 0.2
        
        return min(confidence, 1.0)
