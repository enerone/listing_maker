from typing import Dict, Any
from .base_agent import BaseAgent
from ..models import AgentResponse, ProductInput

class ProductAnalysisAgent(BaseAgent):
    """
    Agente especializado en analizar productos, categorización y variantes
    Responde a la pregunta 1: ¿Cómo se llama exactamente el producto, en qué categoría de Amazon pensás listarlo y qué variantes ofrece?
    """
    
    def __init__(self):
        super().__init__("ProductAnalysisAgent", temperature=0.3)
    
    def get_system_prompt(self) -> str:
        return """
        Eres un experto en análisis de productos para Amazon. Tu tarea es analizar la información del producto y proporcionar:
        
        1. Análisis del nombre del producto y optimizaciones sugeridas
        2. Categorización precisa en Amazon
        3. Identificación y estructuración de variantes (colores, talles, modelos)
        4. Subcategorías y clasificaciones relevantes
        5. Atributos del producto importantes para Amazon
        
        IMPORTANTE: Responde únicamente con un objeto JSON válido con la siguiente estructura:
        {
            "product_name_analysis": {
                "original_name": "string",
                "optimized_name": "string",
                "optimization_reasons": ["string"]
            },
            "category_analysis": {
                "primary_category": "string",
                "subcategories": ["string"],
                "amazon_browse_nodes": ["string"],
                "category_confidence": 0.95
            },
            "variants_analysis": {
                "has_variants": true/false,
                "variant_types": ["size", "color", "model"],
                "structured_variants": [
                    {
                        "type": "color",
                        "values": ["red", "blue", "green"],
                        "impact_on_listing": "string"
                    }
                ],
                "variant_strategy": "string"
            },
            "product_attributes": {
                "brand_requirements": "string",
                "key_attributes": {"attribute": "value"},
                "required_compliance": ["string"]
            },
            "confidence_score": 0.95,
            "recommendations": ["string"]
        }
        """
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa la información del producto para análisis y categorización
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
            Analiza el siguiente producto para Amazon:
            
            INFORMACIÓN DEL PRODUCTO:
            - Nombre: {product_input.product_name}
            - Categoría sugerida: {product_input.category}
            - Variantes disponibles: {[str(v.dict()) for v in product_input.variants]}
            - Propuesta de valor: {product_input.value_proposition}
            - Ventajas competitivas: {product_input.competitive_advantages}
            
            CONTEXTO ADICIONAL:
            - Cliente objetivo: {product_input.target_customer_description}
            - Situaciones de uso: {product_input.use_situations}
            - Especificaciones: {product_input.raw_specifications}
            
            Proporciona un análisis completo del producto, su categorización óptima en Amazon, 
            y estrategia de variantes basado en esta información.
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
                    "product_name_analysis": {
                        "original_name": product_input.product_name,
                        "optimized_name": product_input.product_name,
                        "optimization_reasons": ["Análisis manual requerido"]
                    },
                    "category_analysis": {
                        "primary_category": str(product_input.category),
                        "subcategories": [],
                        "amazon_browse_nodes": [],
                        "category_confidence": 0.5
                    },
                    "variants_analysis": {
                        "has_variants": len(product_input.variants) > 0,
                        "variant_types": [],
                        "structured_variants": [],
                        "variant_strategy": "Revisión manual necesaria"
                    },
                    "product_attributes": {
                        "brand_requirements": "Por determinar",
                        "key_attributes": {},
                        "required_compliance": []
                    },
                    "confidence_score": 0.5,
                    "recommendations": ["Revisar manualmente el análisis del producto"]
                }
                
                return self._create_agent_response(
                    data=fallback_data,
                    confidence=0.5,
                    status="partial",
                    processing_time=response["processing_time"],
                    notes=["Error parseando respuesta de IA, usando datos base"],
                    recommendations=["Revisar manualmente el análisis del producto"]
                )
                
        except Exception as e:
            return self._create_agent_response(
                data={},
                confidence=0.0,
                status="error",
                notes=[f"Error procesando: {str(e)}"],
                recommendations=["Revisar datos de entrada y reintentar"]
            )
