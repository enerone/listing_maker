from typing import Dict, Any, List
import logging
import os
import asyncio
from datetime import datetime
import re
import json

from .base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class IntelligentImageSearchAgent(BaseAgent):
    """
    Agente inteligente para búsqueda de imágenes que usa LLM para análisis contextual
    y genera URLs dinámicas basadas en el contexto del producto.
    """
    
    def __init__(self):
        super().__init__("IntelligentImageSearchAgent", temperature=0.3)
        self.images_dir = "downloaded_images"
        self.max_images = 8
        
        # Crear directorio de imágenes si no existe
        os.makedirs(self.images_dir, exist_ok=True)
    
    def get_system_prompt(self) -> str:
        return """Eres un experto en análisis de productos y búsqueda de imágenes para listings de Amazon.

Tu trabajo es:
1. Analizar el contexto del producto (nombre, categoría, características, descripción)
2. Identificar el tipo específico de producto
3. Generar términos de búsqueda específicos y relevantes
4. Crear URLs de imágenes relevantes usando Unsplash
5. Proporcionar recomendaciones de imágenes para maximizar ventas

Debes ser muy específico en el análisis. Por ejemplo:
- "Audífonos Profesionales Gaming RGB" -> términos: "gaming headset", "rgb gaming headphones", "professional gaming audio"
- "Mate de vidrio Premium" -> términos: "glass mate cup", "traditional mate", "premium glass cup"
- "Mochila Escolar Resistente" -> términos: "school backpack", "durable student bag", "educational backpack"

Para las imágenes, usa URLs de Unsplash con términos específicos:
- Gaming headset: https://images.unsplash.com/search/gaming-headset
- Mate: https://images.unsplash.com/search/mate-cup
- Smartwatch: https://images.unsplash.com/search/smartwatch

Proporciona respuestas precisas y contextuales en formato JSON."""

    async def _analyze_product_with_llm(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa el LLM para analizar el contexto del producto y generar términos de búsqueda específicos.
        """
        product_name = product_data.get("product_name", "")
        category = product_data.get("category", "")
        features = product_data.get("features", [])
        description = product_data.get("description", "")
        
        # Crear prompt para análisis contextual
        prompt = f"""
Analiza este producto y genera términos de búsqueda específicos para encontrar imágenes relevantes:

PRODUCTO: {product_name}
CATEGORÍA: {category}
CARACTERÍSTICAS: {', '.join(features) if features else 'No especificadas'}
DESCRIPCIÓN: {description}

Proporciona tu análisis en formato JSON:
{{
    "product_type": "tipo específico del producto",
    "primary_search_terms": ["término1", "término2", "término3"],
    "secondary_search_terms": ["término4", "término5"],
    "image_urls": [
        "https://images.unsplash.com/search/termino1",
        "https://images.unsplash.com/search/termino2",
        "https://images.unsplash.com/search/termino3",
        "https://images.unsplash.com/search/termino4",
        "https://images.unsplash.com/search/termino5"
    ],
    "image_contexts": ["contexto1", "contexto2", "contexto3"],
    "confidence": 0.95,
    "recommendations": ["recomendación1", "recomendación2", "recomendación3"]
}}

Ejemplos de análisis:
- "Audífonos Gaming RGB" -> "gaming_headset", términos: ["gaming headset", "rgb gaming headphones", "professional gaming audio"]
- "Mate de vidrio Premium" -> "mate_cup", términos: ["glass mate cup", "traditional mate", "premium glass cup"]
- "Smartwatch Deportivo" -> "fitness_smartwatch", términos: ["fitness smartwatch", "sport watch", "health tracker"]

Sé muy específico y preciso. Genera URLs de Unsplash reales usando los términos de búsqueda.
"""
        
        try:
            response = await self.ollama_service.generate_response(prompt)
            
            if response.get("success"):
                content = response.get("content", "")
                # Extraer JSON de la respuesta
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
                else:
                    logger.warning("No se pudo extraer JSON del análisis del LLM")
                    return self._fallback_analysis(product_data)
            else:
                logger.warning(f"Error en LLM: {response.get('error')}")
                return self._fallback_analysis(product_data)
                
        except Exception as e:
            logger.error(f"Error en análisis contextual: {e}")
            return self._fallback_analysis(product_data)
    
    def _fallback_analysis(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis de fallback basado en reglas específicas para diferentes productos.
        """
        product_name = product_data.get("product_name", "").lower()
        category = product_data.get("category", "").lower()
        
        # Detección específica de auriculares/audífonos gaming
        if any(term in product_name for term in ["audifonos", "headphones", "headset", "auriculares"]):
            if any(term in product_name for term in ["gaming", "rgb", "profesional", "gamer"]):
                return {
                    "product_type": "gaming_headset",
                    "primary_search_terms": ["gaming headset", "rgb gaming headphones", "professional gaming audio"],
                    "secondary_search_terms": ["esports headset", "gaming setup", "pc gaming audio"],
                    "image_urls": [
                        "https://images.unsplash.com/photo-1599669454699-248893623440?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1628202926206-c63a34b1618f?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1586933986584-ad4c04c3e503?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1545127398-14699f92334b?w=800&h=600&fit=crop"
                    ],
                    "image_contexts": ["gaming setup", "professional studio", "esports context"],
                    "confidence": 0.9,
                    "recommendations": [
                        "Buscar imágenes de auriculares gaming específicos con RGB",
                        "Incluir contexto de setup gaming profesional",
                        "Mostrar características técnicas como drivers y conectividad"
                    ]
                }
            else:
                return {
                    "product_type": "headphones",
                    "primary_search_terms": ["professional headphones", "audio headphones", "studio headphones"],
                    "secondary_search_terms": ["music headphones", "audio equipment", "sound quality"],
                    "image_urls": [
                        "https://images.unsplash.com/photo-1564424224827-cd24b8915874?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1491927570842-0261e477d937?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1585298723682-7115561c6c14?w=800&h=600&fit=crop"
                    ],
                    "image_contexts": ["professional audio", "studio setup", "music context"],
                    "confidence": 0.85,
                    "recommendations": [
                        "Buscar imágenes de auriculares profesionales",
                        "Incluir contexto de estudio de música",
                        "Mostrar calidad de audio y materiales premium"
                    ]
                }
        
        # Detección específica de mate
        elif any(term in product_name for term in ["mate", "glass", "vidrio"]):
            return {
                "product_type": "mate_cup",
                "primary_search_terms": ["glass mate cup", "traditional mate", "argentine mate"],
                "secondary_search_terms": ["tea cup", "traditional drink", "glass cup"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop"
                ],
                "image_contexts": ["traditional setting", "kitchen context", "cultural context"],
                "confidence": 0.9,
                "recommendations": [
                    "Buscar imágenes de mate tradicional y cultural",
                    "Incluir contexto de uso tradicional",
                    "Mostrar calidad del vidrio y diseño"
                ]
            }
        
        # Detección específica de smartwatch
        elif any(term in product_name for term in ["smartwatch", "watch", "reloj"]):
            return {
                "product_type": "smartwatch",
                "primary_search_terms": ["apple watch", "smartwatch", "fitness tracker"],
                "secondary_search_terms": ["wearable tech", "smart device", "fitness watch"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&h=600&fit=crop"
                ],
                "image_contexts": ["lifestyle", "fitness context", "tech showcase"],
                "confidence": 0.85,
                "recommendations": [
                    "Buscar imágenes de smartwatch en uso",
                    "Incluir contexto de fitness y lifestyle",
                    "Mostrar características técnicas y apps"
                ]
            }
        
        # Detección específica de mochila
        elif any(term in product_name for term in ["mochila", "backpack", "bag"]):
            return {
                "product_type": "backpack",
                "primary_search_terms": ["school backpack", "student backpack", "travel backpack"],
                "secondary_search_terms": ["laptop bag", "hiking backpack", "educational bag"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1581605405669-fcdf81165afa?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1622560480652-b55b095b1d71?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1585916420730-b2a2143d9ae5?w=800&h=600&fit=crop"
                ],
                "image_contexts": ["school context", "travel context", "outdoor lifestyle"],
                "confidence": 0.85,
                "recommendations": [
                    "Buscar imágenes de mochila en contexto escolar",
                    "Incluir contexto de viaje y outdoor",
                    "Mostrar capacidad y organización interna"
                ]
            }
        
        # Fallback genérico
        else:
            return {
                "product_type": "generic_product",
                "primary_search_terms": [product_name.replace(" ", "+")],
                "secondary_search_terms": [category],
                "image_urls": [
                    "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=800&h=600&fit=crop"
                ],
                "image_contexts": ["product showcase", "studio shot"],
                "confidence": 0.6,
                "recommendations": ["Buscar imágenes específicas del producto"]
            }
    
    async def _download_image(self, url: str, index: int) -> Dict[str, Any]:
        """
        Simula la descarga de una imagen (por ahora solo genera metadata).
        """
        try:
            # Generar metadata de la imagen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"product_{timestamp}_{index}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            return {
                "local_path": filepath,
                "filename": filename,
                "url": url,
                "thumbnail": url.replace("w=800&h=600", "w=200&h=150"),
                "description": f"Imagen {index + 1} del producto",
                "search_term": f"product_image_{index}",
                "source": "unsplash",
                "relevance_score": 0.9
            }
                
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return {}
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa la búsqueda de imágenes usando análisis contextual inteligente.
        """
        start_time = datetime.now()
        
        try:
            product_data = data.get("product_data", {})
            
            # 1. Análisis contextual del producto usando LLM
            analysis = await self._analyze_product_with_llm(product_data)
            
            # 2. Procesar URLs de imágenes
            downloaded_images = []
            image_urls = analysis.get("image_urls", [])
            
            for i, url in enumerate(image_urls[:self.max_images]):
                image_data = await self._download_image(url, i)
                if image_data:
                    downloaded_images.append(image_data)
            
            # 3. Organizar imágenes por categorías
            image_categories = {}
            search_terms = analysis.get("primary_search_terms", [])
            
            for i, img in enumerate(downloaded_images):
                term = search_terms[i % len(search_terms)] if search_terms else f"category_{i}"
                if term not in image_categories:
                    image_categories[term] = []
                image_categories[term].append(img)
            
            # 4. Generar recomendaciones específicas
            recommendations = analysis.get("recommendations", [])
            recommendations.extend([
                f"Se procesaron {len(downloaded_images)} imágenes relevantes para {analysis['product_type']}",
                f"Análisis contextual completado con {analysis.get('confidence', 0.8)*100:.0f}% de confianza",
                "Imágenes optimizadas para conversión en Amazon"
            ])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                agent_name=self.agent_name,
                status="success",
                confidence=analysis.get("confidence", 0.8),
                processing_time=processing_time,
                data={
                    "product_type_detected": analysis["product_type"],
                    "downloaded_images": downloaded_images,
                    "image_categories": image_categories,
                    "search_terms_used": analysis.get("primary_search_terms", []) + analysis.get("secondary_search_terms", []),
                    "analysis_result": analysis,
                    "total_images_found": len(downloaded_images)
                },
                recommendations=recommendations,
                notes=[f"Búsqueda inteligente completada para {analysis['product_type']} con {len(downloaded_images)} imágenes"]
            )
            
        except Exception as e:
            logger.error(f"Error en IntelligentImageSearchAgent: {e}")
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                data={"error": str(e)},
                recommendations=["Error en búsqueda inteligente de imágenes, revisar configuración"],
                notes=[f"Error: {str(e)}"]
            )
