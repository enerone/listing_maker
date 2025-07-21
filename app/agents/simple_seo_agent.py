"""
Agente SEO simplificado que genera keywords de manera más robusta
"""
from typing import Dict, Any, List
import logging
import time
from .base_agent import BaseAgent
from ..models import ProductInput, AgentResponse

logger = logging.getLogger(__name__)

class SimpleSEOAgent(BaseAgent):
    """
    Agente SEO simplificado que se enfoca solo en generar keywords
    """
    
    def __init__(self, temperature: float = 0.3):
        super().__init__(
            agent_name="Simple SEO Agent",
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema simplificado para generar keywords
        """
        return """Eres un experto en SEO para Amazon. Tu trabajo es generar keywords relevantes en español para productos.
Responde siempre con una lista simple de keywords separadas por comas.
No uses formato JSON, solo keywords separadas por comas.
Genera entre 10-15 keywords relevantes."""
    
    async def process(self, product_input: ProductInput) -> AgentResponse:
        """
        Genera keywords de manera simple y robusta
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generando keywords para: {product_input.product_name}")
            
            # Crear prompt simple
            prompt = self._build_simple_prompt(product_input)
            
            # Generar respuesta sin estructura JSON
            response = await self._generate_response(prompt, structured=False)
            
            if response.get("success"):
                content = response.get("content", "")
                keywords = self._extract_keywords_from_text(content)
                
                # Crear datos estructurados simples
                data = {
                    "seo_strategy": {
                        "primary_keywords": keywords[:5],
                        "secondary_keywords": keywords[5:10],
                        "long_tail_keywords": keywords[10:],
                        "all_keywords": keywords
                    }
                }
                
                processing_time = time.time() - start_time
                
                return AgentResponse(
                    agent_name=self.agent_name,
                    status="success",
                    data=data,
                    confidence=0.8,
                    processing_time=processing_time,
                    notes=[
                        f"Generados {len(keywords)} keywords",
                        "Keywords extraídos del texto de respuesta",
                        "Estrategia SEO básica aplicada"
                    ],
                    recommendations=[
                        "Usar keywords primarios en título",
                        "Distribuir keywords secundarios en bullets",
                        "Incluir keywords de cola larga en descripción"
                    ]
                )
            else:
                raise Exception(f"Error en Ollama: {response.get('error', 'Sin respuesta')}")
            
        except Exception as e:
            logger.error(f"Error en agente SEO simple: {str(e)}")
            processing_time = time.time() - start_time
            
            # Generar keywords de fallback básicos
            fallback_keywords = self._generate_fallback_keywords(product_input)
            
            return AgentResponse(
                agent_name=self.agent_name,
                status="success",
                data={
                    "seo_strategy": {
                        "primary_keywords": fallback_keywords[:3],
                        "secondary_keywords": fallback_keywords[3:6],
                        "long_tail_keywords": fallback_keywords[6:],
                        "all_keywords": fallback_keywords
                    }
                },
                confidence=0.5,
                processing_time=processing_time,
                notes=[f"Error en IA, usando keywords de fallback: {str(e)}"],
                recommendations=["Usar keywords básicos generados"]
            )
    
    def _build_simple_prompt(self, product_input: ProductInput) -> str:
        """
        Construye un prompt simple para generar keywords
        """
        return f"""
Genera keywords SEO en español para este producto de Amazon:

Producto: {product_input.product_name}
Descripción: {product_input.value_proposition}
Categoría: {product_input.category}
Keywords iniciales: {', '.join(product_input.target_keywords) if product_input.target_keywords else 'Ninguno'}

Genera 15 keywords relevantes separados por comas. Incluye:
- Keywords principales del producto
- Sinónimos y variaciones
- Términos de búsqueda populares
- Keywords de cola larga específicos

Solo responde con la lista de keywords separados por comas, sin explicaciones.
"""
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extrae keywords del texto de respuesta
        """
        try:
            # Limpiar el texto
            text = text.strip()
            
            # Dividir por comas, puntos y comas, o saltos de línea
            import re
            keywords = re.split(r'[,;\n]', text)
            
            # Limpiar cada keyword
            cleaned_keywords = []
            for kw in keywords:
                kw = kw.strip().lower()
                # Remover números al inicio, guiones, etc.
                kw = re.sub(r'^\d+[\.\-\)]\s*', '', kw)
                if kw and len(kw) > 2 and len(kw) < 50:
                    cleaned_keywords.append(kw)
            
            # Remover duplicados manteniendo el orden
            unique_keywords = []
            seen = set()
            for kw in cleaned_keywords:
                if kw not in seen:
                    unique_keywords.append(kw)
                    seen.add(kw)
            
            return unique_keywords[:15]
            
        except Exception as e:
            logger.error(f"Error extrayendo keywords: {str(e)}")
            return []
    
    def _generate_fallback_keywords(self, product_input: ProductInput) -> List[str]:
        """
        Genera keywords de fallback básicos cuando falla la IA
        """
        fallback = []
        
        # Keywords del nombre del producto
        name_words = product_input.product_name.lower().split()
        fallback.extend(name_words)
        
        # Keywords de la categoría
        category_map = {
            "ELECTRONICS": ["electronico", "tecnologia", "gadget"],
            "CLOTHING": ["ropa", "vestimenta", "fashion"],
            "BOOKS": ["libro", "lectura", "literatura"],
            "HOME": ["hogar", "casa", "domestico"],
            "BEAUTY": ["belleza", "cosmetico", "cuidado"],
            "SPORTS": ["deporte", "fitness", "ejercicio"]
        }
        
        if product_input.category and product_input.category.name in category_map:
            fallback.extend(category_map[product_input.category.name])
        
        # Keywords iniciales del usuario
        if product_input.target_keywords:
            fallback.extend(product_input.target_keywords)
        
        # Keywords genéricos útiles
        fallback.extend([
            "calidad", "profesional", "premium", "resistente", 
            "original", "garantia", "amazon", "oferta"
        ])
        
        # Limpiar y deduplicar
        unique_fallback = []
        seen = set()
        for kw in fallback:
            kw = kw.lower().strip()
            if kw and len(kw) > 2 and kw not in seen:
                unique_fallback.append(kw)
                seen.add(kw)
        
        return unique_fallback[:12]
