from typing import Dict, Any, List
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class ProductDescriptionAgent(BaseAgent):
    """
    Agente especializado en generar descripciones largas y detalladas del producto.
    
    Responsabilidades:
    - Crear descripciones completas y atractivas del producto
    - Incorporar beneficios emocionales y funcionales
    - Optimizar para conversión en Amazon
    - Generar contenido que complementa los bullet points
    """
    
    def __init__(self, temperature: float = 0.6):
        super().__init__(
            agent_name="Product Description Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para el agente de descripción de producto
        """
        return """Eres un experto copywriter especializado en crear descripciones de productos para Amazon. 
Tu trabajo es generar descripciones largas, atractivas y persuasivas que conviertan navegadores en compradores.
Te especializas en storytelling de productos, beneficios emocionales y llamadas a la acción.
Siempre devuelves respuestas en formato JSON válido.
Eres creativo, persuasivo y enfocado en la conversión.
IMPORTANTE: Todas las recomendaciones deben estar completamente en español, con un lenguaje claro y específico para el mercado hispanohablante."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Procesa la información del producto y genera una descripción completa
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando generación de descripción para: {product_input.product_name}")
            
            # Preparar prompt especializado para descripción
            prompt = self._build_description_prompt(product_input)
            
            # Generar respuesta con Ollama
            parsed_response = await self._generate_response(prompt, structured=True)
            
            if parsed_response:
                # Calcular confianza basada en la calidad de la descripción
                confidence = self._calculate_description_confidence(parsed_response)
                
                processing_time = time.time() - start_time
                
                return AgentResponse(
                    agent_name=self.agent_name,
                    status="success",
                    confidence=confidence,
                    processing_time=processing_time,
                    data=parsed_response,
                    notes=[
                        "Descripción completa generada",
                        "Storytelling incorporado",
                        "Beneficios emocionales incluidos",
                        "Call-to-action optimizado"
                    ]
                )
            else:
                return AgentResponse(
                    agent_name=self.agent_name,
                    status="error",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    data={"error": "No se pudo generar descripción"},
                    notes=["Error al generar descripción del producto"]
                )
        
        except Exception as e:
            logger.error(f"Error en ProductDescriptionAgent: {str(e)}")
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                confidence=0.0,
                processing_time=time.time() - start_time,
                data={"error": str(e)},
                notes=[f"Error inesperado: {str(e)}"]
            )
    
    def _build_description_prompt(self, product_input: ProductInput) -> str:
        """
        Construye el prompt para generar descripción del producto
        """
        return f"""
INFORMACIÓN DEL PRODUCTO:
- Nombre: {product_input.product_name}
- Categoría: {product_input.category}
- Propuesta de valor: {product_input.value_proposition}
- Cliente objetivo: {product_input.target_customer_description}
- Situaciones de uso: {', '.join(product_input.use_situations)}
- Ventajas competitivas: {', '.join(product_input.competitive_advantages)}
- Especificaciones: {product_input.raw_specifications}
- Contenido de la caja: {product_input.box_content_description}
- Garantía: {product_input.warranty_info}
- Precio objetivo: ${product_input.target_price}

TAREA:
Genera una descripción completa, extensa y altamente persuasiva del producto que use EXCLUSIVAMENTE párrafos narrativos fluidos y storytelling emocional.

FORMATO DE RESPUESTA (JSON):
{{
    "main_description": {{
        "opening_hook": "Párrafo introductorio de 4-5 oraciones que capture inmediatamente la atención con una historia, problema o escenario relatable que conecte emocionalmente con el cliente",
        "product_story": "Historia narrativa de 5-6 oraciones que cuente la génesis del producto, su propósito y cómo transforma la vida del usuario, creando conexión emocional",
        "key_benefits_expanded": "Párrafo detallado de 6-8 oraciones que explique los principales beneficios de manera fluida, usando ejemplos específicos y casos de uso reales",
        "use_case_scenarios": "Descripción narrativa de 5-6 oraciones de múltiples escenarios específicos donde el producto mejora dramáticamente la experiencia del cliente",
        "competitive_advantages": "Párrafo de 4-5 oraciones explicando por qué este producto es superior, usando comparaciones sutiles y ventajas únicas",
        "technical_benefits": "Párrafo de 4-5 oraciones que traduzca las especificaciones técnicas en beneficios tangibles y comprensibles para el usuario",
        "lifestyle_integration": "Párrafo de 4-5 oraciones que describa cómo el producto se integra perfectamente en el estilo de vida del cliente objetivo",
        "social_proof": "Párrafo de 3-4 oraciones que genere confianza mencionando garantías, calidad premium y satisfacción del cliente",
        "call_to_action": "Párrafo final de 3-4 oraciones que motive la compra de manera persuasiva pero elegante, creando urgencia sutil"
    }},
    "full_description": "Descripción completa unificada de 800-1200 palabras en formato párrafo continuo, sin bullet points, que combine toda la información de manera fluida y narrativa para usar directamente en Amazon. Debe leer como un texto publicitario profesional que cuenta una historia convincente sobre el producto, sus beneficios y cómo transforma la vida del usuario. Incluye storytelling emocional, beneficios específicos, casos de uso detallados y una llamada a la acción persuasiva.",
    "description_variants": [
        "Versión corta: párrafo intenso de 200-300 palabras enfocado en el beneficio principal",
        "Versión media: descripción equilibrada de 400-600 palabras con storytelling y beneficios clave",
        "Versión larga: descripción completa de 800-1200 palabras con narrativa completa y todos los elementos persuasivos"
    ],
    "emotional_triggers": [
        "Primer gatillo emocional específico con explicación",
        "Segundo gatillo emocional que conecte con aspiraciones",
        "Tercer gatillo emocional que genere urgencia o exclusividad",
        "Cuarto gatillo emocional que inspire confianza"
    ],
    "power_words": [
        "Primera palabra/frase poderosa para captar atención",
        "Segunda palabra/frase que genere deseo",
        "Tercera palabra/frase que inspire acción",
        "Cuarta palabra/frase que transmita calidad"
    ],
    "recommendations": [
        "Sugerencia específica para mejorar la narrativa",
        "Elemento emocional adicional que podría agregarse",
        "Optimización específica para Amazon y conversión",
        "Mejora en storytelling o conectividad emocional"
    ]
}}

INSTRUCCIONES CRÍTICAS PARA DESCRIPCIÓN PERSUASIVA:
- NUNCA uses bullet points (•), guiones (-), números (1,2,3) o cualquier formato de lista
- SIEMPRE escribe en párrafos narrativos fluidos y extensos
- Cada párrafo debe tener 4-8 oraciones completas y bien conectadas
- Usa conectores narrativos como "Además", "Por otra parte", "Imagina que", "Lo que hace especial"
- Enfócate en beneficios emocionales antes que características técnicas
- Crea una narrativa cohesiva que enganche desde la primera línea
- El texto debe leerse como una historia persuasiva del producto
- La descripción completa debe ser un texto continuo de mínimo 800 palabras
- Incluye storytelling que haga al cliente verse usando el producto
- Usa lenguaje sensorial y emotivo
- Genera urgencia sutil sin ser agresivo
- Incluye prueba social y elementos de confianza

EJEMPLO DE ESTILO NARRATIVO DESEADO:
"Imagina despertar cada mañana con la confianza de saber que tu día está perfectamente organizado. Nuestra innovadora mochila resistente al agua no es solo un accesorio más, es tu compañero de aventuras que entiende que la vida moderna demanda versatilidad sin sacrificar estilo. Diseñada para los profesionales ambiciosos que se niegan a elegir entre funcionalidad y elegancia, esta mochila representa la evolución del transporte personal inteligente. Su construcción premium con materiales resistentes al agua te libera de la preocupación constante por el clima, permitiéndote enfocarte en lo que realmente importa: conquistar tus metas diarias. Cada compartimento ha sido meticulosamente diseñado para crear orden en el caos de la vida moderna, transformando tu rutina diaria en una experiencia fluida y placentera..."

ELEMENTOS OBLIGATORIOS A INCLUIR:
- Historia/narrativa que conecte emocionalmente
- Beneficios específicos traducidos desde las características técnicas
- Escenarios de uso detallados y visuales
- Comparación sutil con alternativas inferiores
- Elementos de confianza y calidad premium
- Llamada a la acción que inspire sin presionar
- Lenguaje sensorial y emocional
- Mínimo 800 palabras en la descripción completa

EVITA COMPLETAMENTE:
- Cualquier formato de lista o enumeración
- Frases técnicas sin contexto emocional
- Lenguaje genérico o aburrido
- Texto fragmentado o desconectado
- Descripciones menores a 500 palabras
- Falta de storytelling o narrativa
"""
    
    def _calculate_description_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza de la descripción generada
        """
        confidence = 0.0
        
        # Verificar descripción principal (60% del peso)
        main_desc = data.get("main_description", {})
        main_sections = ["opening_hook", "product_story", "key_benefits_expanded", "call_to_action"]
        for section in main_sections:
            if main_desc.get(section) and len(main_desc.get(section, "")) > 80:
                confidence += 0.15
        
        # Verificar descripción completa (25% del peso)
        full_desc = data.get("full_description", "")
        if len(full_desc) >= 800:
            confidence += 0.25
        elif len(full_desc) >= 500:
            confidence += 0.15
        elif len(full_desc) >= 300:
            confidence += 0.1
        
        # Verificar elementos adicionales (15% del peso)
        if len(data.get("emotional_triggers", [])) >= 3:
            confidence += 0.1
        if len(data.get("description_variants", [])) >= 3:
            confidence += 0.05
        
        return min(confidence, 1.0)
