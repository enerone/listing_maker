from typing import Dict, Any, List
import logging
import os
import asyncio
import aiohttp
import json
from datetime import datetime
import re

from .base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class DynamicImageSearchAgent(BaseAgent):
    """
    Agente dinámico para búsqueda de imágenes que usa LLM para análisis contextual
    y APIs dinámicas para obtener imágenes relevantes.
    """
    
    def __init__(self):
        super().__init__("DynamicImageSearchAgent", temperature=0.3)
        self.images_dir = "downloaded_images"
        self.max_images = 8
        
        # Configuración para Unsplash API
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.unsplash_base_url = "https://api.unsplash.com"
        
        # Configuración para Pixabay API (alternativa)
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        self.pixabay_base_url = "https://pixabay.com/api/"
        
        # Crear directorio de imágenes si no existe
        os.makedirs(self.images_dir, exist_ok=True)
    
    def get_system_prompt(self) -> str:
        return """Eres un experto en análisis de productos y búsqueda de imágenes para listings de Amazon.

Tu trabajo es:
1. Analizar el contexto del producto (nombre, categoría, características, descripción)
2. Identificar el tipo específico de producto
3. Generar términos de búsqueda específicos y relevantes
4. Proporcionar recomendaciones de imágenes para maximizar ventas

Debes ser muy específico en el análisis. Por ejemplo:
- "Audífonos Profesionales Gaming" -> términos: "gaming headset", "professional headphones", "rgb gaming headphones"
- "Mate de vidrio" -> términos: "glass mate cup", "traditional mate", "argentine mate"
- "Mochila Escolar" -> términos: "school backpack", "student backpack", "educational bag"

Proporciona respuestas precisas y contextuales."""

    async def _analyze_product_context(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
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
    "image_contexts": ["contexto1", "contexto2", "contexto3"],
    "avoid_terms": ["término_a_evitar1", "término_a_evitar2"],
    "confidence": 0.95,
    "recommendations": ["recomendación1", "recomendación2"]
}}

Ejemplos de análisis:
- Audífonos Gaming -> "gaming_headset", términos: ["gaming headset", "professional headphones", "rgb headphones"]
- Mate de vidrio -> "mate_cup", términos: ["glass mate cup", "traditional mate", "argentine mate"]
- Smartwatch -> "smartwatch", términos: ["apple watch", "fitness tracker", "smart watch"]

Sé muy específico y preciso.
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
        Análisis de fallback basado en reglas simples.
        """
        product_name = product_data.get("product_name", "").lower()
        category = product_data.get("category", "").lower()
        
        # Detección básica de tipo de producto
        if any(term in product_name for term in ["audifonos", "headphones", "headset", "auriculares"]):
            return {
                "product_type": "gaming_headset" if "gaming" in product_name else "headphones",
                "primary_search_terms": ["gaming headset", "professional headphones", "rgb headphones"],
                "secondary_search_terms": ["gaming setup", "pc gaming", "esports gear"],
                "image_contexts": ["gaming setup", "professional studio", "product showcase"],
                "avoid_terms": ["generic electronics", "random tech"],
                "confidence": 0.8,
                "recommendations": ["Buscar imágenes de auriculares gaming específicos", "Incluir contexto de gaming setup"]
            }
        elif any(term in product_name for term in ["mate", "glass"]):
            return {
                "product_type": "mate_cup",
                "primary_search_terms": ["glass mate cup", "traditional mate", "argentine mate"],
                "secondary_search_terms": ["tea cup", "traditional drink", "glass cup"],
                "image_contexts": ["traditional setting", "kitchen context", "cultural context"],
                "avoid_terms": ["generic cup", "random drinks"],
                "confidence": 0.8,
                "recommendations": ["Buscar imágenes de mate tradicional", "Incluir contexto cultural"]
            }
        elif any(term in product_name for term in ["smartwatch", "watch"]):
            return {
                "product_type": "smartwatch",
                "primary_search_terms": ["apple watch", "smartwatch", "fitness tracker"],
                "secondary_search_terms": ["wearable tech", "smart device", "fitness watch"],
                "image_contexts": ["lifestyle", "fitness context", "tech showcase"],
                "avoid_terms": ["generic electronics", "random gadgets"],
                "confidence": 0.8,
                "recommendations": ["Buscar imágenes de smartwatch específico", "Incluir contexto de fitness"]
            }
        else:
            return {
                "product_type": "generic_product",
                "primary_search_terms": [product_name.replace(" ", "+")],
                "secondary_search_terms": [category],
                "image_contexts": ["product showcase", "studio shot"],
                "avoid_terms": ["irrelevant", "generic"],
                "confidence": 0.6,
                "recommendations": ["Buscar imágenes específicas del producto"]
            }
    
    async def _search_unsplash_images(self, search_terms: List[str], per_page: int = 8) -> List[Dict[str, Any]]:
        """
        Busca imágenes en Unsplash usando los términos de búsqueda generados.
        """
        if not self.unsplash_access_key:
            logger.warning("Unsplash API key no configurada")
            return []
        
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for term in search_terms[:3]:  # Limitar a 3 términos principales
                    url = f"{self.unsplash_base_url}/search/photos"
                    params = {
                        "query": term,
                        "per_page": per_page // len(search_terms[:3]),
                        "orientation": "landscape",
                        "content_filter": "high"
                    }
                    headers = {
                        "Authorization": f"Client-ID {self.unsplash_access_key}"
                    }
                    
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            for photo in data.get("results", []):
                                images.append({
                                    "url": photo["urls"]["regular"],
                                    "thumbnail": photo["urls"]["thumb"],
                                    "description": photo.get("description", ""),
                                    "alt_description": photo.get("alt_description", ""),
                                    "search_term": term,
                                    "source": "unsplash",
                                    "id": photo["id"]
                                })
                        else:
                            logger.warning(f"Error en Unsplash API: {response.status}")
                
        except Exception as e:
            logger.error(f"Error buscando en Unsplash: {e}")
        
        return images[:per_page]
    
    async def _search_pixabay_images(self, search_terms: List[str], per_page: int = 8) -> List[Dict[str, Any]]:
        """
        Busca imágenes en Pixabay como alternativa a Unsplash.
        """
        if not self.pixabay_api_key:
            logger.warning("Pixabay API key no configurada")
            return []
        
        images = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for term in search_terms[:3]:
                    url = self.pixabay_base_url
                    params = {
                        "key": self.pixabay_api_key,
                        "q": term,
                        "image_type": "photo",
                        "orientation": "horizontal",
                        "category": "all",
                        "per_page": per_page // len(search_terms[:3]),
                        "safesearch": "true"
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for photo in data.get("hits", []):
                                images.append({
                                    "url": photo["largeImageURL"],
                                    "thumbnail": photo["previewURL"],
                                    "description": photo.get("tags", ""),
                                    "alt_description": photo.get("tags", ""),
                                    "search_term": term,
                                    "source": "pixabay",
                                    "id": photo["id"]
                                })
                        else:
                            logger.warning(f"Error en Pixabay API: {response.status}")
                
        except Exception as e:
            logger.error(f"Error buscando en Pixabay: {e}")
        
        return images[:per_page]
    
    async def _download_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Descarga una imagen y la guarda localmente.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_data["url"]) as response:
                    if response.status == 200:
                        # Generar nombre único para la imagen
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_extension = image_data["url"].split(".")[-1].split("?")[0]
                        filename = f"product_{timestamp}_{image_data['id']}.{file_extension}"
                        filepath = os.path.join(self.images_dir, filename)
                        
                        # Guardar imagen usando aiofiles
                        import aiofiles
                        async with aiofiles.open(filepath, "wb") as f:
                            await f.write(await response.read())
                        
                        return {
                            "local_path": filepath,
                            "filename": filename,
                            "url": image_data["url"],
                            "thumbnail": image_data["thumbnail"],
                            "description": image_data["description"],
                            "search_term": image_data["search_term"],
                            "source": image_data["source"],
                            "relevance_score": 0.8  # Será calculado por el LLM
                        }
                    else:
                        logger.warning(f"Error descargando imagen: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error descargando imagen: {e}")
            return {}
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa la búsqueda de imágenes usando análisis contextual dinámico.
        """
        start_time = datetime.now()
        
        try:
            product_data = data.get("product_data", {})
            
            # 1. Análisis contextual del producto
            analysis = await self._analyze_product_context(product_data)
            
            # 2. Buscar imágenes usando los términos generados
            all_search_terms = analysis["primary_search_terms"] + analysis["secondary_search_terms"]
            
            # Intentar Unsplash primero, luego Pixabay como fallback
            images = await self._search_unsplash_images(all_search_terms)
            if not images:
                images = await self._search_pixabay_images(all_search_terms)
            
            # 3. Descargar imágenes seleccionadas
            downloaded_images = []
            download_tasks = []
            
            for image in images[:self.max_images]:
                task = self._download_image(image)
                download_tasks.append(task)
            
            # Ejecutar descargas en paralelo
            download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            for result in download_results:
                if result and not isinstance(result, Exception):
                    downloaded_images.append(result)
            
            # 4. Organizar imágenes por categorías
            image_categories = {}
            for img in downloaded_images:
                search_term = img.get("search_term", "other")
                if search_term not in image_categories:
                    image_categories[search_term] = []
                image_categories[search_term].append(img)
            
            # 5. Generar recomendaciones específicas
            recommendations = analysis.get("recommendations", [])
            recommendations.extend([
                f"Se encontraron {len(downloaded_images)} imágenes relevantes para {analysis['product_type']}",
                f"Términos de búsqueda más efectivos: {', '.join(analysis['primary_search_terms'])}",
                "Considera agregar imágenes de contexto de uso del producto"
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
                    "search_terms_used": all_search_terms,
                    "analysis_result": analysis,
                    "total_images_found": len(downloaded_images)
                },
                recommendations=recommendations,
                notes=[f"Búsqueda dinámica completada para {analysis['product_type']} con {len(downloaded_images)} imágenes"]
            )
            
        except Exception as e:
            logger.error(f"Error en DynamicImageSearchAgent: {e}")
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                data={"error": str(e)},
                recommendations=["Error en búsqueda de imágenes, revisar configuración de APIs"],
                notes=[f"Error: {str(e)}"]
            )
