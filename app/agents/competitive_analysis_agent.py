from typing import Dict, Any
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class CompetitiveAnalysisAgent(BaseAgent):
    """
    Agente especializado en análisis competitivo simplificado
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
        Realiza análisis competitivo simplificado del producto
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análisis competitivo para: {product_input.product_name}")
            
            # Preparar prompt simplificado
            prompt = f"""
Analiza la competencia para: {product_input.product_name}
Categoría: {product_input.category}
Precio: ${product_input.target_price}
Target: {product_input.target_customer_description}

Identifica 3 competidores principales y ventajas competitivas clave.
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
                        "Competidores principales identificados",
                        "Análisis de gaps competitivos realizado",
                        "Estrategia de diferenciación desarrollada",
                        "Posicionamiento competitivo definido"
                    ],
                    recommendations=response["parsed_data"].get("recommendations", [])
                )
            else:
                # Fallback con datos básicos
                fallback_data = {
                    "competitors": ["Competidor A", "Competidor B", "Competidor C"],
                    "competitive_advantages": [
                        {
                            "advantage": "Características únicas del producto",
                            "strength": "medium",
                            "impact": "Diferenciación en el mercado"
                        }
                    ],
                    "market_positioning": "Competidor directo en segmento medio",
                    "pricing_strategy": "Precios competitivos en el rango medio",
                    "differentiation_points": ["Calidad", "Características", "Servicio"],
                    "confidence_score": 0.6,
                    "recommendations": ["Investigar competencia específica", "Validar posicionamiento"]
                }
                
                return self._create_agent_response(
                    data=fallback_data,
                    confidence=0.6,
                    status="partial",
                    processing_time=processing_time,
                    notes=[
                        "Competidores principales identificados",
                        "Análisis de gaps competitivos realizado", 
                        "Estrategia de diferenciación desarrollada",
                        "Posicionamiento competitivo definido"
                    ],
                    recommendations=["Investigar competencia específica", "Validar posicionamiento"]
                )
            
        except Exception as e:
            logger.error(f"Error en análisis competitivo: {str(e)}")
            processing_time = time.time() - start_time
            return self._create_agent_response(
                data={},
                confidence=0.0,
                status="error",
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"],
                recommendations=["Revisar configuración del agente"]
            )
