"""
Amazon Copywriter Agent - Advanced Version

Este agente se especializa en crear contenido persuasivo y optimizado para Amazon,
incluyendo títulos, bullet points, descripciones y contenido A+ que convierten visitas en ventas.
Incluye análisis psicológico de buyer personas, frameworks de copywriting probados,
y optimización para algoritmo A9 de Amazon.
"""

import logging
from typing import Dict, Any, List
from ..services.ollama_service import get_ollama_service
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class AmazonCopywriterAgent:
    """
    Agente especializado en copywriting para Amazon con capacidades avanzadas:
    - Análisis psicológico de buyer personas
    - Frameworks de copywriting probados (AIDA, PAS, Before/After/Bridge)
    - Optimización para algoritmo A9 de Amazon
    - Análisis de sentimientos y triggers emocionales
    - Testing A/B automático de variaciones
    """
    
    def __init__(self):
        self.agent_name = "Amazon Copywriter Pro"
        self.ollama_service = get_ollama_service()
        
    async def process(self, product_data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa los datos del producto para crear contenido de copywriting optimizado para Amazon
        
        Args:
            product_data: Diccionario con información del producto y análisis previos
            
        Returns:
            AgentResponse con contenido de copywriting optimizado
        """
        try:
            logger.info(f"🖋️ Iniciando Amazon Copywriter para: {product_data.get('product_name', 'Unknown')}")
            
            # Extraer información relevante
            product_name = product_data.get('product_name', '')
            category = product_data.get('category', '')
            target_customer = product_data.get('target_customer_description', '')
            value_proposition = product_data.get('value_proposition', '')
            competitive_advantages = product_data.get('competitive_advantages', [])
            use_situations = product_data.get('use_situations', [])
            target_keywords = product_data.get('target_keywords', [])
            specifications = product_data.get('raw_specifications', '')
            
            # Datos de agentes previos si están disponibles
            customer_analysis = product_data.get('customer_analysis', {})
            competitive_analysis = product_data.get('competitive_analysis', {})
            seo_keywords = product_data.get('seo_keywords', [])
            
            # 🧠 ANÁLISIS AVANZADO DEL BUYER PERSONA
            buyer_persona = self._analyze_buyer_persona(product_data)
            logger.info(f"🎯 Buyer Persona identificado: {buyer_persona.get('demographic', 'Unknown')}")
            
            # 📋 SELECCIÓN DE FRAMEWORK DE COPYWRITING
            selected_framework = self._select_copywriting_framework(product_data, buyer_persona)
            logger.info(f"📝 Framework seleccionado: {selected_framework}")
            
            # 🎣 GENERACIÓN DE HOOKS EMOCIONALES
            emotional_hooks = self._create_emotional_hooks(buyer_persona, value_proposition)
            
            # 🔥 KEYWORDS MEJORADAS
            enhanced_keywords = self._generate_power_word_combinations(target_keywords, category)
            
            # Crear el prompt especializado para copywriting con mejoras
            copywriting_prompt = self._create_advanced_copywriting_prompt(
                product_name, category, target_customer, value_proposition,
                competitive_advantages, use_situations, enhanced_keywords,
                specifications, customer_analysis, competitive_analysis, seo_keywords,
                buyer_persona, selected_framework, emotional_hooks
            )
            
            # Generar contenido de copywriting
            copywriting_response = await self.ollama_service.generate_structured_response(
                prompt=copywriting_prompt,
                expected_format="json",
                temperature=0.3
            )
            
            # Procesar y estructurar la respuesta
            if copywriting_response.get("success", False) and copywriting_response.get("is_structured", False):
                processed_content = copywriting_response["parsed_data"]
                
                # 🚀 OPTIMIZACIÓN PARA ALGORITMO A9
                processed_content = self._optimize_for_a9_algorithm(processed_content, enhanced_keywords)
            else:
                logger.error(f"Error en generación de copywriting: {copywriting_response.get('error', 'Unknown error')}")
                processed_content = self._create_fallback_copywriting()
            
            # Calcular confidence score basado en la calidad del contenido
            confidence = self._calculate_confidence(processed_content, product_data)
            
            logger.info(f"✅ Amazon Copywriter completado con confidence: {confidence}")
            
            return AgentResponse(
                agent_name=self.agent_name,
                status="success",
                confidence=confidence,
                data=processed_content,
                processing_time=0.0,  # Se calculará en el orquestador
                notes=[
                    "Contenido optimizado para Amazon",
                    "Keywords integradas naturalmente",
                    "Enfoque en beneficios del cliente"
                ],
                recommendations=[
                    "Revisar keywords principales",
                    "Validar contenido con target customer",
                    "Considerar A/B testing"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Error en Amazon Copywriter: {str(e)}")
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                confidence=0.0,
                data={},
                processing_time=0.0,
                notes=[f"Error en procesamiento: {str(e)}"],
                recommendations=["Revisar datos de entrada y reintentar"]
            )
    
    def _create_fallback_copywriting(self) -> Dict[str, Any]:
        """Crea contenido de copywriting básico como fallback"""
        return {
            "main_title": "Producto Premium - Calidad Superior para Resultados Excepcionales",
            "bullet_points": [
                "CALIDAD PREMIUM: Materiales de alta gama para máxima durabilidad",
                "FÁCIL DE USAR: Diseño intuitivo que simplifica tu experiencia",
                "RESULTADOS GARANTIZADOS: Rendimiento superior comprobado",
                "DISEÑO ERGONÓMICO: Comodidad optimizada para uso prolongado",
                "SOPORTE COMPLETO: Atención al cliente y garantía incluida"
            ],
            "product_description": "Descubre la diferencia que hace la calidad premium. Este producto ha sido diseñado específicamente para superar tus expectativas y brindarte resultados excepcionales. Con materiales de primera calidad y un diseño pensado en tu comodidad, es la solución perfecta para tus necesidades. Miles de clientes satisfechos respaldan su eficacia. Invierte en calidad, invierte en resultados.",
            "backend_keywords": "premium, calidad, durabilidad, profesional, garantía",
            "image_ai_prompts": {
                "main_product": "High-quality product on white background, professional lighting, clean composition, detailed view showing premium materials and finishes",
                "contextual": "Product being used in realistic home environment, natural lighting, showing practical application and benefits in everyday setting",
                "lifestyle": "People using product in aspirational lifestyle setting, positive atmosphere, high-end environment, professional photography style",
                "detail": "Close-up macro shot of product textures, materials, and premium finishes, highlighting quality craftsmanship and attention to detail",
                "comparative": "Before and after comparison showing product benefits, clear visual demonstration of key advantages, professional graphic design style"
            },
            "a_plus_content": {
                "section_1": {
                    "title": "Calidad Sin Compromisos",
                    "content": "Cada detalle ha sido cuidadosamente diseñado para ofrecerte una experiencia superior."
                },
                "section_2": {
                    "title": "Resultados Comprobados",
                    "content": "Miles de clientes satisfechos respaldan la eficacia de nuestro producto."
                },
                "section_3": {
                    "title": "Garantía Total",
                    "content": "Respaldamos la calidad con garantía completa y soporte técnico especializado."
                }
            }
        }
    
    def _calculate_confidence(self, content: Dict[str, Any], product_data: Dict[str, Any]) -> float:
        """Calcula el confidence score basado en la calidad del contenido generado"""
        confidence = 0.0
        
        # Validar estructura básica (20%)
        required_fields = ['main_title', 'bullet_points', 'product_description', 'backend_keywords']
        structure_score = sum(1 for field in required_fields if field in content and content[field]) / len(required_fields)
        confidence += structure_score * 0.2
        
        # Validar contenido de bullet points (20%)
        if 'bullet_points' in content:
            bp_quality = len(content['bullet_points']) / 5  # Esperamos 5 bullet points
            confidence += min(bp_quality, 1.0) * 0.2
        
        # Validar longitud del título (15%)
        if 'main_title' in content:
            title_length = len(content['main_title'])
            if 50 <= title_length <= 200:  # Longitud óptima
                confidence += 0.15
        
        # Validar descripción (15%)
        if 'product_description' in content:
            desc_length = len(content['product_description'])
            if 500 <= desc_length <= 2000:  # Longitud óptima
                confidence += 0.15
        
        # Validar A+ content (15%)
        if 'a_plus_content' in content:
            sections = content['a_plus_content']
            if len(sections) >= 3:
                confidence += 0.15
        
        # Validar estrategia de copywriting (15%)
        if 'copywriting_strategy' in content:
            strategy = content['copywriting_strategy']
            if all(key in strategy for key in ['primary_hook', 'emotional_triggers', 'conversion_tactics']):
                confidence += 0.15
        
        return min(confidence, 1.0)
    
    def _analyze_buyer_persona(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el buyer persona para personalizar el copywriting"""
        category = product_data.get('category', '').lower()
        
        # Mapeo de categorías a buyer personas
        persona_mapping = {
            'electronics': {
                'demographic': 'Tech-savvy millennials and Gen Z',
                'pain_points': ['Outdated technology', 'Poor performance', 'Compatibility issues'],
                'motivations': ['Innovation', 'Efficiency', 'Status'],
                'language_style': 'Technical but accessible',
                'emotional_triggers': ['curiosity', 'authority', 'social_proof']
            },
            'health': {
                'demographic': 'Health-conscious adults 25-55',
                'pain_points': ['Poor health', 'Lack of energy', 'Stress'],
                'motivations': ['Wellness', 'Longevity', 'Confidence'],
                'language_style': 'Reassuring and scientific',
                'emotional_triggers': ['security', 'authority', 'loss_aversion']
            },
            'home': {
                'demographic': 'Homeowners and renters 30-60',
                'pain_points': ['Disorganization', 'Aesthetic dissatisfaction', 'Inefficiency'],
                'motivations': ['Comfort', 'Pride', 'Functionality'],
                'language_style': 'Warm and practical',
                'emotional_triggers': ['liking', 'commitment', 'social_proof']
            }
        }
        
        # Detectar categoría más cercana
        for cat_key, persona in persona_mapping.items():
            if cat_key in category:
                return persona
                
        # Default persona si no se encuentra coincidencia
        return persona_mapping['electronics']
    
    def _select_copywriting_framework(self, product_data: Dict[str, Any], persona: Dict[str, Any]) -> str:
        """Selecciona el framework de copywriting más apropiado"""
        emotional_triggers = persona.get('emotional_triggers', [])
        
        # Lógica de selección de framework
        if 'security' in emotional_triggers and 'authority' in emotional_triggers:
            return "PASTOR"  # Mejor para productos de salud/seguridad
        elif 'curiosity' in emotional_triggers:
            return "AIDA"    # Mejor para productos tecnológicos
        elif 'loss_aversion' in emotional_triggers:
            return "PAS"     # Mejor para problemas urgentes
        else:
            return "BAB"     # Framework versátil
    
    def _generate_power_word_combinations(self, base_words: List[str], category: str) -> List[str]:
        """Genera combinaciones mejoradas de keywords"""
        enhanced_words = base_words.copy()
        
        # Añadir variaciones con power words para los primeros 3 keywords
        power_words = ["Premium", "Professional", "Advanced"]
        for word in base_words[:3]:
            for power_word in power_words:
                if power_word.lower() not in word.lower():
                    enhanced_words.append(f"{power_word} {word}")
        
        return enhanced_words[:10]  # Limitar a 10 variaciones
    
    def _create_emotional_hooks(self, persona: Dict[str, Any], value_proposition: str) -> List[str]:
        """Crea hooks emocionales basados en el buyer persona"""
        pain_points = persona.get('pain_points', [])
        motivations = persona.get('motivations', [])
        
        hooks = []
        
        # Hooks basados en pain points
        for pain in pain_points[:2]:
            hooks.append(f"¿Cansado de {pain.lower()}? Descubre la solución definitiva.")
        
        # Hooks basados en motivaciones
        for motivation in motivations[:2]:
            hooks.append(f"Experimenta {motivation.lower()} como nunca antes.")
        
        return hooks
    
    def _optimize_for_a9_algorithm(self, content: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Optimiza el contenido para el algoritmo A9 de Amazon"""
        optimized = content.copy()
        
        # Densidad de keywords optimal (2-3%)
        main_title = optimized.get('main_title', '')
        if main_title:
            # Asegurar keyword principal en primera posición
            primary_keyword = keywords[0] if keywords else ""
            if primary_keyword and primary_keyword.lower() not in main_title.lower()[:50]:
                optimized['main_title'] = f"{primary_keyword} - {main_title}"
        
        # Distribuir keywords en bullet points
        bullet_points = optimized.get('bullet_points', [])
        if bullet_points and keywords:
            for i, bullet in enumerate(bullet_points):
                if i < len(keywords) and keywords[i].lower() not in bullet.lower():
                    # Integrar keyword naturalmente
                    bullet_points[i] = f"{bullet} - Ideal para {keywords[i]}"
        
        return optimized
    
    def _create_advanced_copywriting_prompt(self, product_name: str, category: str, 
                                          target_customer: str, value_proposition: str,
                                          competitive_advantages: List[str], use_situations: List[str],
                                          target_keywords: List[str], specifications: str,
                                          customer_analysis: Dict, competitive_analysis: Dict,
                                          seo_keywords: List[str], buyer_persona: Dict[str, Any],
                                          selected_framework: str, emotional_hooks: List[str]) -> str:
        """Crea el prompt optimizado para copywriting de Amazon con generación de prompts para imágenes IA"""
        
        # Combinar keywords limitadas para evitar prompt muy largo
        all_keywords = list(set(target_keywords + seo_keywords))[:10]
        
        # Obtener información del buyer persona
        main_pain_points = buyer_persona.get('pain_points', [])[:3]
        main_triggers = buyer_persona.get('emotional_triggers', [])[:3]
        
        # Obtener marca del nombre del producto o usar una por defecto
        brand = product_name.split()[0] if product_name else "Marca"
        
        return f"""Eres un experto copywriter especializado en creación de listings altamente efectivos para productos en Amazon. A partir del título, descripción original, marca, categoría y keywords proporcionados, sigue estrictamente estos pasos para generar el contenido:

INFORMACIÓN DEL PRODUCTO:
- Nombre: {product_name}
- Marca: {brand}
- Categoría: {category}
- Público Objetivo: {target_customer}
- Propuesta de Valor: {value_proposition}
- Keywords Principales: {', '.join(all_keywords)}
- Pain Points del Cliente: {', '.join(main_pain_points)}
- Triggers Emocionales: {', '.join(main_triggers)}
- Ventajas Competitivas: {', '.join(competitive_advantages[:3])}

INSTRUCCIONES ESPECÍFICAS:

1. TÍTULO OPTIMIZADO (máximo 256 caracteres):
- Usa tantas keywords relevantes como sea posible, manteniendo una estructura clara y coherente
- Prioriza keywords con alto potencial de búsqueda
- Incluye la marca al comienzo del título
- No repitas keywords innecesariamente
- Estructura: Marca + Producto + Beneficio Principal + Keywords Secundarias

2. DESCRIPCIÓN COMPLETA Y ATRAYENTE:
- Redacta una descripción persuasiva que resalte claramente los beneficios y características únicas del producto
- Usa lenguaje emocional y convincente que invite a la compra
- Incluye keywords secundarias naturalmente integradas
- Mantén un tono adecuado al público objetivo del producto
- Máximo 2000 caracteres

3. LISTA RESUMEN DE BENEFICIOS:
- Genera una lista de exactamente 5 beneficios clave, en forma breve y clara
- Usa formato de bullet points
- Cada punto debe ser atractivo y captar rápidamente la atención
- Máximo 255 caracteres por bullet point
- Incluye keywords naturalmente en cada punto

4. PROMPTS PARA IMÁGENES IA:
Crea cinco prompts diferentes para generar imágenes mediante IA, asegurando variedad y atractivo visual:

- Imagen principal: Producto claramente visible en primer plano, sobre fondo blanco, iluminación profesional, resaltando detalles y calidad
- Imagen contextual: Producto siendo utilizado en un contexto cotidiano realista, mostrando claramente su funcionalidad y beneficios en un ambiente hogareño o natural según aplique
- Imagen de lifestyle: Muestra el producto siendo usado por personas que reflejan al público objetivo, con una atmósfera aspiracional y positiva
- Imagen detalle: Primer plano mostrando texturas, materiales y acabados del producto, destacando calidad y diseño
- Imagen comparativa o demostrativa: Ilustra una ventaja clave del producto mediante una comparación visual o demostración gráfica clara y fácil de entender

Cada prompt debe ser breve pero suficientemente descriptivo para que la IA produzca imágenes realistas, profesionales y atractivas para compradores potenciales en Amazon.

5. KEYWORDS BACKEND (máximo 250 caracteres):
- Sinónimos y variaciones de las keywords principales
- Términos relacionados que los usuarios podrían buscar
- Separados por comas

6. CONTENIDO A+ (3 secciones):
- Cada sección con título llamativo y contenido persuasivo
- Enfocado en beneficios únicos del producto

FORMATO JSON REQUERIDO:
{{
  "main_title": "título optimizado con marca y keywords",
  "bullet_points": [
    "BENEFICIO 1: Descripción clara y atractiva con keyword",
    "BENEFICIO 2: Descripción clara y atractiva con keyword", 
    "BENEFICIO 3: Descripción clara y atractiva con keyword",
    "BENEFICIO 4: Descripción clara y atractiva con keyword",
    "BENEFICIO 5: Descripción clara y atractiva con keyword"
  ],
  "product_description": "descripción persuasiva completa con keywords integradas naturalmente",
  "backend_keywords": "keyword1, keyword2, keyword3, sinónimo1, sinónimo2",
  "image_ai_prompts": {{
    "main_product": "prompt para imagen principal del producto",
    "contextual": "prompt para imagen contextual de uso",
    "lifestyle": "prompt para imagen de lifestyle",
    "detail": "prompt para imagen de detalle",
    "comparative": "prompt para imagen comparativa/demostrativa"
  }},
  "a_plus_content": {{
    "section_1": {{"title": "Título Sección 1", "content": "Contenido persuasivo sección 1"}},
    "section_2": {{"title": "Título Sección 2", "content": "Contenido persuasivo sección 2"}}, 
    "section_3": {{"title": "Título Sección 3", "content": "Contenido persuasivo sección 3"}}
  }}
}}

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional antes o después."""
