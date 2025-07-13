from typing import Dict, Any, List
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class TechnicalSpecsAgent(BaseAgent):
    """
    Agente especializado en procesar especificaciones técnicas y requisitos del producto.
    
    Responsabilidades:
    - Extraer y organizar especificaciones técnicas
    - Identificar dimensiones, peso, materiales
    - Determinar compatibilidades y requisitos
    - Generar bullets técnicos para Amazon
    """
    
    def __init__(self, temperature: float = 0.3):
        super().__init__(
            agent_name="Technical Specs Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de especificaciones técnicas
        """
        return """Eres un experto en especificaciones técnicas de productos para Amazon. 
Tu trabajo es extraer, organizar y presentar las especificaciones técnicas de forma clara y vendedora.
Siempre devuelves respuestas en formato JSON válido.
Eres preciso con números, medidas y datos técnicos.
Priorizas información técnica que influya en la decisión de compra."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Procesa las especificaciones técnicas del producto
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análisis técnico para: {product_input.product_name}")
            
            # Preparar prompt especializado para especificaciones técnicas
            prompt = self._build_technical_prompt(product_input)
            
            # Generar respuesta con Ollama
            parsed_response = await self._generate_response(prompt, structured=True)
            
            processing_time = time.time() - start_time
            
            # Crear respuesta del agente
            response = AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data=parsed_response,
                confidence=self._calculate_technical_confidence(parsed_response),
                processing_time=processing_time,
                notes=[
                    "Especificaciones técnicas procesadas",
                    "Dimensiones y peso extraídos",
                    "Compatibilidades identificadas",
                    "Bullets técnicos generados"
                ],
                recommendations=parsed_response.get("recommendations", [])
            )
            
            logger.info(f"Análisis técnico completado con confianza: {response.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error en análisis técnico: {str(e)}")
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                data={},
                confidence=0.0,
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"]
            )
    
    def _build_technical_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt especializado para análisis técnico
        """
        return f"""
Eres un experto en especificaciones técnicas de productos para Amazon. Analiza la siguiente información del producto y extrae las especificaciones técnicas más relevantes para un listing de Amazon.

INFORMACIÓN DEL PRODUCTO:
Nombre: {product_input.product_name}
Categoría: {product_input.category}
Precio objetivo: ${product_input.target_price}
Especificaciones técnicas: {product_input.raw_specifications}
Descripción del cliente objetivo: {product_input.target_customer_description}
Propuesta de valor: {product_input.value_proposition}
Ventajas competitivas: {', '.join(product_input.competitive_advantages)}
Contenido de la caja: {product_input.box_content_description}
Certificaciones: {', '.join(product_input.certifications) if product_input.certifications else 'Ninguna especificada'}

TAREA:
Analiza las especificaciones técnicas proporcionadas y genera un análisis técnico completo que incluya:

1. **Especificaciones principales** (dimensiones, peso, materiales, etc.)
2. **Compatibilidades y requisitos** del sistema
3. **Bullets técnicos** optimizados para Amazon
4. **Información de certificaciones** relevantes
5. **Recomendaciones técnicas** para el listing

FORMATO DE RESPUESTA (JSON):
{{
    "main_specifications": {{
        "dimensions": "Dimensiones exactas del producto extraídas del texto",
        "weight": "Peso del producto si está disponible",
        "materials": ["Lista", "de", "materiales", "identificados"],
        "power_requirements": "Requisitos de energía si aplica",
        "operating_conditions": "Condiciones de operación extraídas"
    }},
    "compatibility": {{
        "devices": ["Dispositivos", "compatibles", "mencionados"],
        "operating_systems": ["Sistemas", "operativos", "compatibles"],
        "requirements": ["Requisitos", "mínimos", "identificados"]
    }},
    "technical_bullets": [
        "📐 Bullet técnico con dimensiones exactas si disponibles",
        "⚡ Bullet sobre especificaciones de poder/energía",
        "🔧 Bullet sobre compatibilidad",
        "📊 Bullet sobre performance técnico",
        "✅ Bullet sobre certificaciones/estándares"
    ],
    "certifications": [
        "Certificaciones relevantes mencionadas o inferidas"
    ],
    "technical_highlights": [
        "Aspectos técnicos más vendedores",
        "Diferenciadores técnicos clave extraídos"
    ],
    "recommendations": [
        "Recomendaciones para mejorar especificaciones",
        "Información técnica faltante a agregar"
    ]
}}

INSTRUCCIONES IMPORTANTES:
- Extrae información real de los datos proporcionados, no inventes especificaciones
- Si no hay información específica, indica "No especificado" o deja listas vacías
- Los bullets técnicos deben ser específicos y vendedores
- Usa emojis relevantes y números específicos cuando estén disponibles
- Prioriza especificaciones que influyan en la decisión de compra
"""
    
    def _get_technical_schema(self) -> Dict[str, Any]:
        """
        Define el esquema esperado para la respuesta técnica
        """
        return {
            "main_specifications": {
                "dimensions": str,
                "weight": str,
                "materials": list,
                "power_requirements": str,
                "operating_conditions": str
            },
            "compatibility": {
                "devices": list,
                "operating_systems": list,
                "requirements": list
            },
            "technical_bullets": list,
            "certifications": list,
            "technical_highlights": list,
            "recommendations": list
        }
    
    def _calculate_technical_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza del análisis técnico
        """
        confidence = 0.0
        
        # Verificar especificaciones principales
        specs = data.get("main_specifications", {})
        if specs.get("dimensions") and specs.get("dimensions") != "No especificado":
            confidence += 0.2
        if specs.get("weight") and specs.get("weight") != "No especificado":
            confidence += 0.15
        if specs.get("materials") and len(specs.get("materials", [])) > 0:
            confidence += 0.15
        
        # Verificar compatibilidad
        compat = data.get("compatibility", {})
        if compat.get("devices") and len(compat.get("devices", [])) > 0:
            confidence += 0.15
        if compat.get("requirements") and len(compat.get("requirements", [])) > 0:
            confidence += 0.1
        
        # Verificar bullets técnicos
        bullets = data.get("technical_bullets", [])
        if len(bullets) >= 3:
            confidence += 0.15
        elif len(bullets) >= 1:
            confidence += 0.1
        
        # Verificar highlights técnicos
        highlights = data.get("technical_highlights", [])
        if len(highlights) >= 2:
            confidence += 0.1
        elif len(highlights) >= 1:
            confidence += 0.05
        
        return min(confidence, 1.0)
