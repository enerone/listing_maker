from typing import Dict, Any
from .base_agent import BaseAgent
from ..models import AgentResponse, ProductInput

class ValuePropositionAgent(BaseAgent):
    """
    Agente especializado en análisis de propuesta de valor y diferenciación
    Responde a la pregunta 3: ¿Cuál es su propuesta de valor diferencial frente a la competencia?
    """
    
    def __init__(self):
        super().__init__("ValuePropositionAgent", temperature=0.4)
    
    def get_system_prompt(self) -> str:
        return """
        Eres un experto en estrategia de producto y análisis competitivo. Tu tarea es analizar y optimizar la propuesta de valor del producto para Amazon.
        
        Debes proporcionar:
        1. Análisis de la propuesta de valor actual
        2. Identificación de diferenciadores clave
        3. Análisis competitivo en Amazon
        4. Beneficios únicos y ventajas competitivas
        5. Posicionamiento estratégico
        6. Argumentos de venta únicos (USPs)
        
        IMPORTANTE: Responde únicamente con un objeto JSON válido con la siguiente estructura:
        {
            "value_proposition_analysis": {
                "core_value_proposition": "string",
                "primary_benefits": ["string"],
                "secondary_benefits": ["string"],
                "emotional_benefits": ["string"],
                "functional_benefits": ["string"]
            },
            "competitive_analysis": {
                "key_competitors": ["string"],
                "competitive_advantages": [
                    {
                        "advantage": "string",
                        "strength": "high/medium/low",
                        "customer_impact": "string",
                        "defensibility": "string"
                    }
                ],
                "market_gaps": ["string"],
                "price_positioning": "premium/mid-range/budget",
                "unique_features": ["string"]
            },
            "differentiation_strategy": {
                "primary_differentiators": ["string"],
                "secondary_differentiators": ["string"],
                "feature_comparison": {
                    "superior_features": ["string"],
                    "unique_features": ["string"],
                    "standard_features": ["string"]
                },
                "quality_indicators": ["string"]
            },
            "unique_selling_propositions": [
                {
                    "usp": "string",
                    "supporting_evidence": ["string"],
                    "target_segment": "string",
                    "communication_priority": "high/medium/low"
                }
            ],
            "positioning_strategy": {
                "market_position": "string",
                "brand_perception": "string",
                "target_positioning": "string",
                "messaging_hierarchy": ["string"]
            },
            "amazon_specific_advantages": {
                "listing_advantages": ["string"],
                "search_advantages": ["string"],
                "conversion_advantages": ["string"],
                "review_potential": "string"
            },
            "confidence_score": 0.95,
            "recommendations": ["string"]
        }
        """
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa la información del producto para análisis de propuesta de valor
        """
        try:
            # Extraer datos del input
            # El data ya es un ProductInput, no necesitamos recrearlo
            if isinstance(data, ProductInput):
                product_input = data
            else:
                # Solo si viene como dict, lo convertimos
                product_input = ProductInput(**data)
            
            # Construir prompt específico
            prompt = f"""
            Analiza la propuesta de valor y diferenciación competitiva para el siguiente producto en Amazon:
            
            INFORMACIÓN DEL PRODUCTO:
            - Nombre: {product_input.product_name}
            - Categoría: {product_input.category}
            - Precio objetivo: ${product_input.target_price}
            
            PROPUESTA DE VALOR ACTUAL:
            - Propuesta principal: {product_input.value_proposition}
            - Ventajas competitivas: {product_input.competitive_advantages}
            
            CONTEXTO DEL CLIENTE:
            - Cliente objetivo: {product_input.target_customer_description}
            - Situaciones de uso: {product_input.use_situations}
            
            INFORMACIÓN ADICIONAL:
            - Especificaciones: {product_input.raw_specifications}
            - Estrategia de precios: {product_input.pricing_strategy_notes}
            - Palabras clave objetivo: {product_input.target_keywords}
            
            Desarrolla un análisis completo de la propuesta de valor, identificando diferenciadores únicos,
            ventajas competitivas en Amazon, y estrategias de posicionamiento que maximicen las conversiones
            y la competitividad en la plataforma.
            
            Considera factores específicos de Amazon como:
            - Algoritmo de búsqueda A9
            - Factores de ranking de productos
            - Comportamiento de compra en e-commerce
            - Competencia directa e indirecta en la categoría
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
                    "value_proposition_analysis": {
                        "core_value_proposition": product_input.value_proposition,
                        "primary_benefits": product_input.competitive_advantages,
                        "secondary_benefits": [],
                        "emotional_benefits": [],
                        "functional_benefits": product_input.competitive_advantages
                    },
                    "competitive_analysis": {
                        "key_competitors": [],
                        "competitive_advantages": [
                            {
                                "advantage": adv,
                                "strength": "medium",
                                "customer_impact": "Por analizar",
                                "defensibility": "Por evaluar"
                            } for adv in product_input.competitive_advantages
                        ],
                        "market_gaps": [],
                        "price_positioning": "mid-range",
                        "unique_features": []
                    },
                    "differentiation_strategy": {
                        "primary_differentiators": product_input.competitive_advantages,
                        "secondary_differentiators": [],
                        "feature_comparison": {
                            "superior_features": [],
                            "unique_features": [],
                            "standard_features": []
                        },
                        "quality_indicators": []
                    },
                    "unique_selling_propositions": [
                        {
                            "usp": product_input.value_proposition,
                            "supporting_evidence": product_input.competitive_advantages,
                            "target_segment": "Principal",
                            "communication_priority": "high"
                        }
                    ],
                    "positioning_strategy": {
                        "market_position": "Por definir",
                        "brand_perception": "Por analizar",
                        "target_positioning": "Calidad y valor",
                        "messaging_hierarchy": [product_input.value_proposition]
                    },
                    "amazon_specific_advantages": {
                        "listing_advantages": [],
                        "search_advantages": [],
                        "conversion_advantages": [],
                        "review_potential": "Por evaluar"
                    },
                    "confidence_score": 0.5,
                    "recommendations": ["Revisar manualmente el análisis de propuesta de valor"]
                }
                
                return self._create_agent_response(
                    data=fallback_data,
                    confidence=0.5,
                    status="partial",
                    processing_time=response["processing_time"],
                    notes=["Error parseando respuesta de IA, usando datos base"],
                    recommendations=["Revisar manualmente el análisis de propuesta de valor"]
                )
                
        except Exception as e:
            return self._create_agent_response(
                data={},
                confidence=0.0,
                status="error",
                notes=[f"Error procesando: {str(e)}"],
                recommendations=["Revisar datos de entrada y reintentar"]
            )
