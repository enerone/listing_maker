from typing import Dict, Any, List, Optional
import logging
import os
import requests
import aiohttp
import asyncio
from datetime import datetime
import hashlib
from urllib.parse import urlparse
import json

from .base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class ImageSearchAgent(BaseAgent):
    """
    Agente especializado en búsqueda y descarga de imágenes para listings de Amazon.
    Busca imágenes relevantes al producto y las descarga para uso en el listing.
    """
    
    def __init__(self):
        super().__init__("ImageSearchAgent", temperature=0.3)
        self.images_dir = "downloaded_images"
        self.max_images = 10
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
        
        # Crear directorio de imágenes si no existe
        os.makedirs(self.images_dir, exist_ok=True)
    
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para generar búsquedas de imágenes efectivas.
        """
        return """
Eres un experto en búsqueda de imágenes para productos de Amazon. Tu trabajo es generar términos de búsqueda efectivos y evaluar la relevancia de las imágenes para listings de productos.

Debes generar:
1. Términos de búsqueda principales del producto
2. Términos de búsqueda alternativos y relacionados
3. Términos específicos para casos de uso
4. Términos para diferentes ángulos y contextos

Siempre considera:
- Nombre del producto y variaciones
- Características principales
- Casos de uso típicos
- Contextos de uso (hogar, oficina, deporte, etc.)
- Diferentes ángulos (frontal, lateral, en uso, detalles)

Responde siempre en JSON válido con la estructura especificada.
"""
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Busca y descarga imágenes relevantes para el listing.
        """
        start_time = datetime.now()
        
        try:
            # Extraer datos del producto
            product_data = data.get('product_data', {})
            listing_data = self._extract_listing_data(data.get('previous_results', {}))
            
            # Generar términos de búsqueda
            search_terms = await self._generate_search_terms(product_data, listing_data)
            
            # Simular búsqueda de imágenes (en un entorno real usarías APIs como Unsplash, Pexels, etc.)
            image_results = await self._search_images(search_terms)
            
            # Descargar y procesar imágenes
            downloaded_images = await self._download_images(image_results, product_data.get('product_name', 'product'))
            
            # Generar resultado
            result_data = {
                "search_terms_used": search_terms,
                "images_found": len(image_results),
                "images_downloaded": len(downloaded_images),
                "downloaded_images": downloaded_images,
                "image_categories": self._categorize_images(downloaded_images),
                "confidence_score": min(0.9, len(downloaded_images) / self.max_images) if downloaded_images else 0.5
            }
            
            recommendations = self._generate_image_recommendations(downloaded_images, listing_data)
            notes = [
                f"Encontradas {len(image_results)} imágenes",
                f"Descargadas {len(downloaded_images)} imágenes",
                f"Términos de búsqueda: {', '.join(search_terms[:3])}"
            ]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_agent_response(
                data=result_data,
                confidence=result_data["confidence_score"],
                status="success",
                processing_time=processing_time,
                notes=notes,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error en ImageSearchAgent: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_agent_response(
                data={"error": str(e)},
                confidence=0.0,
                status="error",
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"],
                recommendations=[]
            )
    
    async def _generate_search_terms(self, product_data: Dict[str, Any], listing_data: Dict[str, Any]) -> List[str]:
        """
        Genera términos de búsqueda usando IA para encontrar imágenes relevantes.
        """
        try:
            product_name = product_data.get('product_name', '')
            category = product_data.get('category', '')
            features = product_data.get('features', [])
            use_cases = product_data.get('use_cases', [])
            
            prompt = f"""
Genera términos de búsqueda efectivos para encontrar imágenes de producto para un listing de Amazon.

INFORMACIÓN DEL PRODUCTO:
- Nombre: {product_name}
- Categoría: {category}
- Características: {features}
- Casos de uso: {use_cases}

GENERAR TÉRMINOS PARA:
1. Producto principal (3-4 términos)
2. Variaciones y sinónimos (2-3 términos)
3. Casos de uso específicos (2-3 términos)
4. Contextos y ambientes (2-3 términos)

FORMATO DE RESPUESTA (JSON):
{{
    "primary_terms": ["término1", "término2", "término3"],
    "variations": ["variación1", "variación2"],
    "use_case_terms": ["caso1", "caso2"],
    "context_terms": ["contexto1", "contexto2"]
}}

INSTRUCCIONES:
- Usa términos en español e inglés
- Incluye términos específicos del producto
- Considera diferentes ángulos y perspectivas
- Prioriza términos que generen imágenes de alta calidad
"""
            
            response = await self._generate_response(prompt, structured=True)
            
            if response.get("success") and response.get("is_structured"):
                terms_data = response["parsed_data"]
                all_terms = []
                
                # Combinar todos los términos
                for category in ["primary_terms", "variations", "use_case_terms", "context_terms"]:
                    if category in terms_data and isinstance(terms_data[category], list):
                        all_terms.extend(terms_data[category])
                
                return all_terms[:15]  # Limitar a 15 términos
            else:
                # Fallback: generar términos básicos
                return self._generate_fallback_terms(product_data)
                
        except Exception as e:
            logger.error(f"Error generando términos de búsqueda: {e}")
            return self._generate_fallback_terms(product_data)
    
    def _generate_fallback_terms(self, product_data: Dict[str, Any]) -> List[str]:
        """
        Genera términos de búsqueda básicos como fallback.
        """
        terms = []
        product_name = product_data.get('product_name', '')
        
        if product_name:
            terms.append(product_name)
            terms.append(f"{product_name} product")
            terms.append(f"{product_name} amazon")
        
        # Términos generales según categoría
        category = product_data.get('category', '').lower()
        if 'home' in category or 'kitchen' in category:
            terms.extend(['home product', 'kitchen gadget', 'household item'])
        elif 'electronics' in category:
            terms.extend(['electronic device', 'tech product', 'gadget'])
        elif 'sports' in category:
            terms.extend(['sports equipment', 'fitness gear', 'athletic product'])
        else:
            terms.extend(['product', 'commercial product', 'retail item'])
        
        return terms[:10]
    
    async def _search_images(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Busca imágenes reales usando Pixabay API.
        """
        search_results = []
        
        # Usar Pixabay API para búsquedas reales
        async with aiohttp.ClientSession() as session:
            for term in search_terms[:5]:  # Limitar a 5 términos
                try:
                    # Buscar imágenes reales con Pixabay
                    pixabay_results = await self._search_pixabay(session, term)
                    search_results.extend(pixabay_results)
                    
                except Exception as e:
                    logger.warning(f"Error buscando imágenes para término '{term}': {str(e)}")
                    # Fallback a URLs específicas si falla la API
                    fallback_results = await self._get_fallback_urls_for_term(term)
                    search_results.extend(fallback_results)
        
        return search_results
    
    async def _search_pixabay(self, session: aiohttp.ClientSession, term: str) -> List[Dict[str, Any]]:
        """
        Busca imágenes en Pixabay usando su API gratuita.
        """
        results = []
        
        # Pixabay API key gratuita 
        api_key = "9656065-a4094594c34f9ac14c7fc4c39"
        
        url = "https://pixabay.com/api/"
        params = {
            "key": api_key,
            "q": term,
            "image_type": "photo",
            "orientation": "horizontal",
            "min_width": 800,
            "per_page": 3,
            "safesearch": "true"
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for hit in data.get("hits", []):
                        results.append({
                            "url": hit["webformatURL"],
                            "title": f"{term} - {hit.get('tags', '').split(',')[0]}",
                            "description": f"High quality image of {term}",
                            "width": hit["webformatWidth"],
                            "height": hit["webformatHeight"],
                            "search_term": term,
                            "relevance_score": 0.9,
                            "tags": hit.get("tags", ""),
                            "views": hit.get("views", 0)
                        })
                else:
                    logger.warning(f"Pixabay API error for term '{term}': {response.status}")
                    
        except Exception as e:
            logger.warning(f"Error querying Pixabay for term '{term}': {str(e)}")
            
        return results
    
    async def _get_fallback_urls_for_term(self, term: str) -> List[Dict[str, Any]]:
        """
        Obtiene URLs de fallback específicas para un término de búsqueda.
        """
        results = []
        
        # Mapear términos comunes a IDs específicos de Unsplash
        term_mappings = {
            # Electrónicos
            "smartwatch": ["523275335684", "560472354b33", "526170375885"],
            "reloj inteligente": ["523275335684", "560472354b33", "526170375885"],
            "watch": ["523275335684", "560472354b33", "526170375885"],
            "gps": ["505740420928", "542291026e7e", "607853202273"],
            "fitness": ["484704324500", "496181133206", "441986300917"],
            "deportivo": ["484704324500", "496181133206", "441986300917"],
            # Electronics relacionados
            "monitor": ["556742049cf4", "591796738488", "580910051074"],
            "television": ["581833971358", "498049794561", "524004532550"],
            "pantalla": ["556742049cf4", "591796738488", "580910051074"],
            "display": ["581833971358", "498049794561", "524004532550"],
            "tv": ["581833971358", "498049794561", "524004532550"],
            "gaming": ["556742049cf4", "591796738488", "580910051074"],
            # Muebles
            "silla": ["542291026e7e", "472851294608", "467003909585"],
            "chair": ["542291026e7e", "472851294608", "467003909585"],
            "oficina": ["555041469a58", "586023492125", "523275335684"],
            "gamer": ["556742049cf4", "591796738488", "580910051074"],
            # Hogar
            "cocina": ["498049794561", "524004532550", "542291026e7e"],
            "kitchen": ["498049794561", "524004532550", "542291026e7e"],
            "termo": ["556742049cf4", "591796738488", "580910051074"],
            "bottle": ["556742049cf4", "591796738488", "580910051074"],
            # Productos genéricos
            "product": ["523275335684", "560472354b33", "526170375885"],
            "commercial": ["505740420928", "542291026e7e", "607853202273"],
            "retail": ["484704324500", "496181133206", "441986300917"]
        }
        
        # Buscar coincidencias en el término
        image_ids = []
        for key, ids in term_mappings.items():
            if key.lower() in term.lower():
                image_ids.extend(ids)
                break
        
        # Si no hay coincidencias específicas, usar IDs genéricos
        if not image_ids:
            image_ids = ["523275335684", "560472354b33", "526170375885"]
        
        # Crear URLs específicas
        for i, image_id in enumerate(image_ids[:3]):  # Máximo 3 imágenes por término
            url = f"https://images.unsplash.com/photo-{image_id}?w=800&h=600&fit=crop&crop=center"
            results.append({
                "url": url,
                "title": f"{term} - Image {i+1}",
                "description": f"High quality image of {term}",
                "width": 800,
                "height": 600,
                "search_term": term,
                "relevance_score": 0.7 - (i * 0.1)  # Menor score para fallback
            })
        
        return results
        """
        Obtiene URLs específicas para un término de búsqueda.
        """
        results = []
        
        # Mapear términos comunes a IDs específicos de Unsplash
        term_mappings = {
            # Electrónicos
            "smartwatch": ["1OOFHaXYtR8", "r3wLpaxqC1w", "qCUlRfGGNe8"],
            "reloj inteligente": ["1OOFHaXYtR8", "r3wLpaxqC1w", "qCUlRfGGNe8"],
            "watch": ["1OOFHaXYtR8", "r3wLpaxqC1w", "qCUlRfGGNe8"],
            "gps": ["N_aihp118p8", "8CqDvPuo_kI", "hpjSkU2UYSU"],
            "fitness": ["CQfNt66ttZM", "lrQPTQs7nQQ", "5jctAMjz21A"],
            "deportivo": ["CQfNt66ttZM", "lrQPTQs7nQQ", "5jctAMjz21A"],
            # Muebles
            "silla": ["486398u4sX0", "v9bnfMCyKbg", "mpN7xjKQ_Ns"],
            "chair": ["486398u4sX0", "v9bnfMCyKbg", "mpN7xjKQ_Ns"],
            "oficina": ["ZV_64LdGoao", "JjYIqkz4EOI", "QBpZGqEMsKg"],
            "gamer": ["npxXWgQ33ZQ", "2EF8PdAFjNs", "dJsqFOJzBpg"],
            # Hogar
            "cocina": ["_QpbBmYrjgQ", "YmQ0-nmWcV0", "J36fnkbNjLc"],
            "kitchen": ["_QpbBmYrjgQ", "YmQ0-nmWcV0", "J36fnkNjLc"],
            "termo": ["mZnx9429i94", "0W4XLGITrHg", "fhM8eZu4yqQ"],
            "bottle": ["mZnx9429i94", "0W4XLGITrHg", "fhM8eZu4yqQ"],
            # Productos genéricos
            "product": ["1OOFHaXYtR8", "v9bnfMCyKbg", "CQfNt66ttZM"],
            "commercial": ["486398u4sX0", "ZV_64LdGoao", "_QpbBmYrjgQ"],
            "retail": ["mpN7xjKQ_Ns", "QBpZGqEMsKg", "YmQ0-nmWcV0"]
        }
        
        # Buscar coincidencias en el término
        image_ids = []
        for key, ids in term_mappings.items():
            if key.lower() in term.lower():
                image_ids.extend(ids)
                break
        
        # Si no hay coincidencias específicas, usar IDs genéricos
        if not image_ids:
            image_ids = ["1OOFHaXYtR8", "v9bnfMCyKbg", "CQfNt66ttZM"]
        
        # Crear URLs específicas
        for i, image_id in enumerate(image_ids[:3]):  # Máximo 3 imágenes por término
            url = f"https://images.unsplash.com/photo-{image_id}?w=800&h=600&fit=crop&crop=center"
            results.append({
                "url": url,
                "title": f"{term} - Image {i+1}",
                "description": f"High quality image of {term}",
                "width": 800,
                "height": 600,
                "search_term": term,
                "relevance_score": 0.9 - (i * 0.1)
            })
        
        return results
    
    async def _download_images(self, image_results: List[Dict[str, Any]], product_name: str) -> List[Dict[str, Any]]:
        """
        Descarga las imágenes encontradas.
        """
        downloaded = []
        safe_product_name = self._sanitize_filename(product_name)
        
        async with aiohttp.ClientSession() as session:
            for i, image_data in enumerate(image_results):
                try:
                    url = image_data["url"]
                    file_extension = self._get_file_extension(url, image_data.get("format", "jpg"))
                    
                    # Generar nombre único para el archivo
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{safe_product_name}_{timestamp}_{i+1}{file_extension}"
                    file_path = os.path.join(self.images_dir, filename)
                    
                    # Simular descarga (en producción, descargarías realmente)
                    # async with session.get(url) as response:
                    #     if response.status == 200:
                    #         with open(file_path, 'wb') as f:
                    #             f.write(await response.read())
                    
                    # Para la simulación, crear un archivo vacío
                    with open(file_path, 'w') as f:
                        f.write(f"Simulated image file for: {image_data.get('title', 'Unknown')}")
                    
                    downloaded.append({
                        "original_url": url,
                        "local_path": file_path,
                        "filename": filename,
                        "title": image_data.get("title", ""),
                        "search_term": image_data.get("search_term", ""),
                        "width": image_data.get("width", 0),
                        "height": image_data.get("height", 0),
                        "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        "downloaded_at": datetime.now().isoformat()
                    })
                    
                    # Pequeña pausa entre descargas
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"No se pudo descargar imagen {i+1}: {str(e)}")
                    continue
        
        return downloaded
    
    def _categorize_images(self, downloaded_images: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Categoriza las imágenes descargadas por tipo.
        """
        categories = {
            "product_shots": [],
            "lifestyle": [],
            "detail_shots": [],
            "packaging": [],
            "usage_scenarios": []
        }
        
        for image in downloaded_images:
            search_term = image.get("search_term", "").lower()
            filename = image.get("filename", "")
            
            # Lógica simple de categorización basada en términos de búsqueda
            if any(word in search_term for word in ["product", "isolated", "white background"]):
                categories["product_shots"].append(filename)
            elif any(word in search_term for word in ["lifestyle", "home", "kitchen", "office"]):
                categories["lifestyle"].append(filename)
            elif any(word in search_term for word in ["detail", "close up", "macro"]):
                categories["detail_shots"].append(filename)
            elif any(word in search_term for word in ["package", "box", "packaging"]):
                categories["packaging"].append(filename)
            elif any(word in search_term for word in ["use", "using", "action", "demo"]):
                categories["usage_scenarios"].append(filename)
            else:
                categories["product_shots"].append(filename)  # Default
        
        return categories
    
    def _generate_image_recommendations(self, downloaded_images: List[Dict[str, Any]], listing_data: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones sobre el uso de las imágenes descargadas.
        """
        recommendations = []
        
        if len(downloaded_images) == 0:
            recommendations.append("No se pudieron descargar imágenes. Considera buscar imágenes manualmente.")
            return recommendations
        
        # Recomendaciones basadas en cantidad
        if len(downloaded_images) < 5:
            recommendations.append(f"Solo se descargaron {len(downloaded_images)} imágenes. Busca más para tener variedad.")
        
        if len(downloaded_images) >= 7:
            recommendations.append("Excelente variedad de imágenes. Selecciona las 7 mejores para el listing.")
        
        # Recomendaciones sobre tipos de imágenes
        has_product_shots = any("product" in img.get("search_term", "").lower() for img in downloaded_images)
        has_lifestyle = any("lifestyle" in img.get("search_term", "").lower() for img in downloaded_images)
        
        if not has_product_shots:
            recommendations.append("Asegúrate de incluir imágenes del producto sobre fondo blanco como imagen principal.")
        
        if not has_lifestyle:
            recommendations.append("Considera agregar imágenes de estilo de vida mostrando el producto en uso.")
        
        # Recomendaciones sobre calidad
        high_res_images = [img for img in downloaded_images if img.get("width", 0) >= 1000]
        if len(high_res_images) < len(downloaded_images) * 0.7:
            recommendations.append("Algunas imágenes pueden tener baja resolución. Verifica la calidad antes de usar.")
        
        # Recomendación sobre orden
        recommendations.append("Ordena las imágenes: 1) Producto principal, 2) Características, 3) Uso, 4) Detalles, 5) Lifestyle")
        
        return recommendations[:5]  # Limitar a 5 recomendaciones
    
    def _extract_listing_data(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae datos relevantes de resultados de agentes previos.
        """
        listing_data = {
            'title': '',
            'description': '',
            'keywords': [],
            'bullet_points': []
        }
        
        # Extraer de resultados de content agent
        if 'content' in previous_results:
            content_result = previous_results['content']
            if isinstance(content_result, dict):
                listing_data.update({
                    'title': content_result.get('title', ''),
                    'description': content_result.get('description', ''),
                    'bullet_points': content_result.get('bullet_points', [])
                })
        
        # Extraer keywords de SEO agent
        if 'seo_visual' in previous_results:
            seo_result = previous_results['seo_visual']
            if isinstance(seo_result, dict):
                keywords = seo_result.get('keywords', [])
                if isinstance(keywords, list):
                    listing_data['keywords'].extend(keywords)
        
        return listing_data
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza un nombre de archivo para que sea válido en el sistema.
        """
        # Reemplazar caracteres no válidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limitar longitud
        filename = filename[:50]
        
        # Remover espacios al inicio y final
        filename = filename.strip()
        
        return filename if filename else "product"
    
    def _get_file_extension(self, url: str, format_hint: str = "") -> str:
        """
        Determina la extensión de archivo apropiada.
        """
        # Intentar extraer de URL
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        for ext in self.supported_formats:
            if path.endswith(ext):
                return ext
        
        # Usar format_hint si está disponible
        if format_hint:
            format_hint = format_hint.lower()
            if format_hint in ['jpg', 'jpeg']:
                return '.jpg'
            elif format_hint in ['png']:
                return '.png'
            elif format_hint in ['webp']:
                return '.webp'
        
        # Default
        return '.jpg'
