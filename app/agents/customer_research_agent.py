from typing import Dict, Any
from .base_agent import BaseAgent
from ..models import AgentResponse, ProductInput

class CustomerResearchAgent(BaseAgent):
    """
    Agente especializado en investigación de clientes y casos de uso
    Responde a la pregunta 2: ¿A qué tipo de cliente va dirigido y en qué situaciones lo usaría?
    """
    
    def __init__(self):
        super().__init__("CustomerResearchAgent", temperature=0.4)
    
    def get_system_prompt(self) -> str:
        return """
        Eres un experto en investigación de clientes y marketing de productos. 
        
        RESPONDE ÚNICAMENTE con un objeto JSON válido. NO incluyas texto adicional.
        
        {
            "target_demographics": {
                "age_ranges": [{"range": "25-35", "percentage": 40, "characteristics": "Descripción"}],
                "gender_distribution": {"male": 50, "female": 50},
                "income_levels": ["middle_class"],
                "education": ["college"],
                "location": ["urban"]
            },
            "psychographics": {
                "lifestyle": ["active"],
                "values": ["quality"],
                "interests": ["technology"],
                "shopping_behavior": ["online_first"]
            },
            "use_cases": [
                "Uso principal del producto",
                "Uso secundario del producto"
            ],
            "buyer_personas": [
                {
                    "name": "Persona 1",
                    "age": 30,
                    "occupation": "Profesional",
                    "key_characteristics": ["característica"],
                    "main_pain_points": ["dolor"],
                    "purchase_motivations": ["motivación"],
                    "preferred_channels": ["Amazon"],
                    "budget_considerations": "Rango de precio"
                }
            ],
            "customer_journey": {
                "awareness_stage": {
                    "triggers": ["trigger"],
                    "information_sources": ["fuente"],
                    "key_concerns": ["preocupación"]
                },
                "consideration_stage": {
                    "comparison_factors": ["factor"],
                    "decision_criteria": ["criterio"],
                    "common_objections": ["objeción"]
                },
                "purchase_stage": {
                    "final_motivators": ["motivador"],
                    "preferred_purchase_method": "Amazon",
                    "price_sensitivity": "moderate"
                }
            },
            "messaging_strategy": {
                "primary_value_propositions": ["propuesta"],
                "emotional_appeals": ["apelación"],
                "rational_benefits": ["beneficio"],
                "communication_tone": "energetic"
            },
            "confidence_score": 0.95,
            "recommendations": ["recomendación"]
        }
        """
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa la información del producto para investigación de clientes
        """
        try:
            # El data ya es un ProductInput, no necesitamos recrearlo
            if isinstance(data, ProductInput):
                product_input = data
            else:
                # Solo si viene como dict, lo convertimos
                product_input = ProductInput(**data)
            
            # Construir prompt específico
            prompt = f"""
            Analiza el siguiente producto para identificar clientes objetivo:
            
            INFORMACIÓN DEL PRODUCTO:
            - Nombre: {product_input.product_name}
            - Categoría: {product_input.category}
            - Cliente objetivo: {product_input.target_customer_description}
            - Propuesta de valor: {product_input.value_proposition}
            - Situaciones de uso: {product_input.use_situations}
            - Ventajas competitivas: {product_input.competitive_advantages}
            
            Proporciona un análisis completo del público objetivo, demographics, psychographics, 
            casos de uso y estrategia de mensajes para este producto.
            """
            
            # Generar respuesta estructurada
            response = await self._generate_response(prompt, structured=True)
            
            if response["success"] and response.get("is_structured", False):
                return self._create_agent_response(
                    data=response["parsed_data"],
                    confidence=response["parsed_data"].get("confidence_score", 0.8),
                    processing_time=response["processing_time"],
                    recommendations=response["parsed_data"].get("recommendations", [])
                )
            else:
                # Fallback si no se pudo parsear el JSON
                fallback_data = {
                    "target_demographics": {
                        "age_ranges": [{"range": "25-45", "percentage": 70, "characteristics": product_input.target_customer_description}],
                        "gender_distribution": {"male": 50, "female": 50},
                        "income_levels": ["middle_class"],
                        "education": ["college"],
                        "location": ["urban"]
                    },
                    "psychographics": {
                        "lifestyle": ["active"],
                        "values": ["quality"],
                        "interests": ["technology"],
                        "shopping_behavior": ["online_first"]
                    },
                    "use_cases": product_input.use_situations if product_input.use_situations else ["Uso general", "Uso profesional"],
                    "buyer_personas": [{
                        "name": "Cliente típico",
                        "age": 35,
                        "occupation": "Por definir",
                        "key_characteristics": ["Por analizar"],
                        "main_pain_points": ["Por identificar"],
                        "purchase_motivations": ["Por determinar"],
                        "preferred_channels": ["Amazon"],
                        "budget_considerations": "Por analizar"
                    }],
                    "customer_journey": {
                        "awareness_stage": {
                            "triggers": ["Necesidad del producto"],
                            "information_sources": ["Búsquedas en línea"],
                            "key_concerns": ["Precio y calidad"]
                        },
                        "consideration_stage": {
                            "comparison_factors": ["Características y precio"],
                            "decision_criteria": ["Valor por dinero"],
                            "common_objections": ["Incertidumbre sobre calidad"]
                        },
                        "purchase_stage": {
                            "final_motivators": ["Conveniencia de compra"],
                            "preferred_purchase_method": "Amazon",
                            "price_sensitivity": "moderate"
                        }
                    },
                    "messaging_strategy": {
                        "primary_value_propositions": [product_input.value_proposition or "Producto de calidad"],
                        "emotional_appeals": ["Confianza y satisfacción"],
                        "rational_benefits": ["Funcionalidad y durabilidad"],
                        "communication_tone": "professional"
                    },
                    "confidence_score": 0.5,
                    "recommendations": ["Revisar manualmente el análisis de clientes"]
                }
                
                return self._create_agent_response(
                    data=fallback_data,
                    confidence=0.5,
                    status="partial",
                    processing_time=response["processing_time"],
                    notes=["Error parseando respuesta de IA, usando datos base"],
                    recommendations=["Revisar manualmente el análisis de clientes"]
                )
                
        except Exception as e:
            return self._create_agent_response(
                data={},
                confidence=0.0,
                status="error",
                notes=[f"Error procesando: {str(e)}"],
                recommendations=["Revisar datos de entrada y reintentar"]
            )
