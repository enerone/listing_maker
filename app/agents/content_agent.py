from typing import Dict, Any, List
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    """
    Agente especializado en gestionar contenido de la caja y garantías.
    
    Responsabilidades:
    - Analizar contenido de la caja del producto
    - Procesar información de garantías y certificaciones
    - Generar descripción clara de lo que recibe el cliente
    - Optimizar contenido para generar confianza en la compra
    """
    
    def __init__(self, temperature: float = 0.4):
        super().__init__(
            agent_name="Content Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de contenido
        """
        return """Eres un experto en presentación de contenido de productos para Amazon. 
Tu trabajo es generar descripciones claras y convincentes de lo que incluye el producto.
Te especializas en crear confianza mostrando el valor completo del paquete.
Siempre devuelves respuestas en formato JSON válido.
Eres claro, preciso y orientado a generar confianza en el comprador."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Procesa el contenido de la caja y información de garantías
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análisis de contenido para: {product_input.product_name}")
            
            # Preparar prompt especializado para contenido
            prompt = self._build_content_prompt(product_input)
            
            # Generar respuesta con Ollama
            parsed_response = await self._generate_response(prompt, structured=True)
            
            processing_time = time.time() - start_time
            
            # Crear respuesta del agente
            response = AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data=parsed_response,
                confidence=self._calculate_content_confidence(parsed_response),
                processing_time=processing_time,
                notes=[
                    "Contenido de la caja procesado",
                    "Información de garantías analizada",
                    "Descripción de valor completo generada",
                    "Elementos de confianza identificados"
                ],
                recommendations=parsed_response.get("recommendations", [])
            )
            
            logger.info(f"Análisis de contenido completado con confianza: {response.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error en análisis de contenido: {str(e)}")
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                data={},
                confidence=0.0,
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"]
            )
    
    def _build_content_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt especializado para análisis de contenido
        """
        return f"""
Eres un experto en presentación de contenido de productos para Amazon. Analiza la siguiente información del producto y genera una descripción completa y atractiva del contenido del paquete.

INFORMACIÓN DEL PRODUCTO:
Nombre: {product_input.product_name}
Categoría: {product_input.category}
Precio objetivo: ${product_input.target_price}
Contenido de la caja: {product_input.box_content_description}
Información de garantía: {product_input.warranty_info}
Certificaciones: {', '.join(product_input.certifications) if product_input.certifications else 'Ninguna especificada'}
Propuesta de valor: {product_input.value_proposition}
Ventajas competitivas: {', '.join(product_input.competitive_advantages)}

TAREA:
Analiza el contenido proporcionado y genera una presentación completa que incluya:

1. **Lista detallada del contenido** de la caja
2. **Información de garantías** y soporte
3. **Certificaciones** y calidad
4. **Bullets de contenido** optimizados para Amazon
5. **Elementos que generan confianza** en la compra

FORMATO DE RESPUESTA (JSON):
{{
    "box_contents": {{
        "main_product": "Producto principal con descripción clara",
        "accessories": ["Lista", "de", "accesorios", "incluidos"],
        "documentation": ["Manuales", "guías", "documentos", "incluidos"],
        "packaging_details": "Descripción del empaque y presentación"
    }},
    "warranty_info": {{
        "warranty_period": "Período de garantía específico",
        "warranty_coverage": "Qué cubre la garantía",
        "warranty_provider": "Quién proporciona la garantía",
        "support_details": "Información de soporte al cliente"
    }},
    "certifications": {{
        "quality_certifications": ["Certificaciones", "de", "calidad"],
        "safety_certifications": ["Certificaciones", "de", "seguridad"],
        "compliance_standards": ["Estándares", "de", "cumplimiento"]
    }},
    "content_bullets": [
        "📦 Bullet mostrando el valor completo del paquete",
        "🎁 Bullet destacando accesorios incluidos",
        "🛡️ Bullet sobre garantía y soporte",
        "✅ Bullet sobre certificaciones y calidad",
        "📚 Bullet sobre documentación y facilidad de uso"
    ],
    "trust_elements": [
        "Elementos que generan confianza",
        "Aspectos que reducen el riesgo de compra",
        "Valores agregados del paquete completo"
    ],
    "value_proposition": {{
        "complete_package_value": "Valor del paquete completo vs competencia",
        "peace_of_mind_factors": ["Factores", "que", "dan", "tranquilidad"],
        "ready_to_use_elements": "Qué está listo para usar inmediatamente"
    }},
    "recommendations": [
        "Sugerencias para mejorar la presentación del contenido",
        "Elementos adicionales que podrían agregarse",
        "Maneras de destacar mejor el valor del paquete"
    ]
}}

INSTRUCCIONES IMPORTANTES:
- Usa la información real proporcionada, no inventes contenido
- Si algo no está especificado, indícalo claramente
- Los bullets deben ser específicos y generar confianza
- Enfócate en el valor completo que recibe el cliente
- Destaca elementos que diferencien de la competencia
- Usa emojis relevantes para hacer más atractiva la presentación
"""
    
    def _calculate_content_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza del análisis de contenido
        """
        confidence = 0.0
        
        # Verificar contenido de la caja
        box = data.get("box_contents", {})
        if box.get("main_product") and box.get("main_product") != "No especificado":
            confidence += 0.2
        if box.get("accessories") and len(box.get("accessories", [])) > 0:
            confidence += 0.15
        if box.get("documentation") and len(box.get("documentation", [])) > 0:
            confidence += 0.1
        
        # Verificar información de garantía
        warranty = data.get("warranty_info", {})
        if warranty.get("warranty_period") and warranty.get("warranty_period") != "No especificado":
            confidence += 0.15
        if warranty.get("warranty_coverage"):
            confidence += 0.1
        
        # Verificar bullets de contenido
        bullets = data.get("content_bullets", [])
        if len(bullets) >= 4:
            confidence += 0.15
        elif len(bullets) >= 2:
            confidence += 0.1
        
        # Verificar elementos de confianza
        trust = data.get("trust_elements", [])
        if len(trust) >= 2:
            confidence += 0.1
        elif len(trust) >= 1:
            confidence += 0.05
        
        # Verificar propuesta de valor
        value_prop = data.get("value_proposition", {})
        if value_prop.get("complete_package_value"):
            confidence += 0.05
        
        return min(confidence, 1.0)
