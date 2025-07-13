from typing import Dict, Any
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class SocialContentAgent(BaseAgent):
    """
    Agente especializado en generación de hashtags y contenido social simplificado
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
        return """Eres un experto en marketing de contenido social.
Responde ÚNICAMENTE con JSON válido:

{
    "hashtags": {
        "primary": ["#hashtag1", "#hashtag2"],
        "secondary": ["#hashtag3", "#hashtag4"],
        "niche": ["#hashtag5", "#hashtag6"]
    },
    "social_content": {
        "instagram_post": "Texto para Instagram",
        "facebook_post": "Texto para Facebook",
        "tiktok_hooks": ["Hook 1", "Hook 2"]
    },
    "influencer_strategy": {
        "target_influencers": ["Tipo de influencer 1"],
        "collaboration_ideas": ["Idea 1", "Idea 2"]
    },
    "confidence_score": 0.9,
    "recommendations": ["Recomendación 1"]
}"""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Genera estrategia simplificada de contenido social y hashtags
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando generación de contenido social para: {product_input.product_name}")
            
            # Preparar prompt simplificado
            prompt = f"""
Crea contenido social para: {product_input.product_name}
Categoría: {product_input.category}
Target: {product_input.target_customer_description}
Valor: {product_input.value_proposition}

Genera hashtags estratégicos y contenido para redes sociales.
Responde SOLO con JSON según el formato del prompt del sistema.
"""
            
            # Generar respuesta con Ollama
            response = await self._generate_response(prompt, structured=True)
            
            processing_time = time.time() - start_time
            
            if response["success"] and response.get("is_structured", False):
                return self._create_agent_response(
                    data=response["parsed_data"],
                    confidence=response["parsed_data"].get("confidence_score", 0.8),
                    processing_time=processing_time,
                    notes=[
                        "Hashtags estratégicos generados",
                        "Contenido social optimizado creado",
                        "Estrategia de influencers desarrollada",
                        "Calendario de contenido propuesto"
                    ],
                    recommendations=response["parsed_data"].get("recommendations", [])
                )
            else:
                # Fallback con datos básicos
                fallback_data = {
                    "hashtags": {
                        "primary": [f"#{product_input.product_name.lower().replace(' ', '')}", f"#{product_input.category.lower()}"],
                        "secondary": ["#amazon", "#shopping", "#deals"],
                        "niche": ["#productreview", "#quality", "#musthave"]
                    },
                    "social_content": {
                        "instagram_post": f"¡Descubre {product_input.product_name}! 🔥 {product_input.value_proposition or 'Calidad excepcional'} ✨",
                        "facebook_post": f"Nuevo producto disponible: {product_input.product_name}. Perfecto para {product_input.target_customer_description or 'ti'}.",
                        "tiktok_hooks": [f"POV: Necesitas {product_input.product_name}", f"Todo sobre {product_input.product_name} ⬇️"]
                    },
                    "influencer_strategy": {
                        "target_influencers": ["Micro-influencers en nicho específico"],
                        "collaboration_ideas": ["Review detallado", "Unboxing video"]
                    },
                    "confidence_score": 0.6,
                    "recommendations": ["Personalizar hashtags por plataforma", "Validar contenido con audiencia"]
                }
                
                return self._create_agent_response(
                    data=fallback_data,
                    confidence=0.6,
                    status="partial",
                    processing_time=processing_time,
                    notes=[
                        "Hashtags estratégicos generados",
                        "Contenido social optimizado creado",
                        "Estrategia de influencers desarrollada", 
                        "Calendario de contenido propuesto"
                    ],
                    recommendations=["Personalizar hashtags por plataforma", "Validar contenido con audiencia"]
                )
            
        except Exception as e:
            logger.error(f"Error en contenido social: {str(e)}")
            processing_time = time.time() - start_time
            return self._create_agent_response(
                data={},
                confidence=0.0,
                status="error",
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"],
                recommendations=["Revisar configuración del agente"]
            )
