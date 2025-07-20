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
import re

from .base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class ImprovedImageSearchAgent(BaseAgent):
    """
    Agente mejorado para búsqueda de imágenes con mejor relevancia de producto.
    """
    
    def __init__(self):
        super().__init__("ImprovedImageSearchAgent", temperature=0.3)
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
"""
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Busca y descarga imágenes relevantes para el listing con mejor relevancia.
        """
        start_time = datetime.now()
        
        try:
            # Extraer datos del producto
            product_data = data.get('product_data', {})
            listing_data = self._extract_listing_data(data.get('previous_results', {}))
            
            # Generar términos de búsqueda específicos (sin Ollama)
            search_terms = self._generate_improved_search_terms(product_data, listing_data)
            
            # Buscar imágenes con mejor relevancia
            image_results = await self._search_images_improved(search_terms, product_data)
            
            # Descargar y procesar imágenes
            downloaded_images = await self._download_images(image_results, product_data.get('product_name', 'product'))
            
            # Generar resultado
            result_data = {
                "search_terms_used": search_terms,
                "images_found": len(image_results),
                "images_downloaded": len(downloaded_images),
                "downloaded_images": downloaded_images,
                "image_categories": self._categorize_images(downloaded_images),
                "confidence_score": min(0.95, len(downloaded_images) / self.max_images) if downloaded_images else 0.3
            }
            
            recommendations = self._generate_image_recommendations(downloaded_images, listing_data)
            notes = [
                f"Encontradas {len(image_results)} imágenes relevantes",
                f"Descargadas {len(downloaded_images)} imágenes",
                f"Términos específicos: {', '.join(search_terms[:3])}"
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
            logger.error(f"Error en ImprovedImageSearchAgent: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_agent_response(
                data={"error": str(e)},
                confidence=0.0,
                status="error",
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"],
                recommendations=[]
            )
    
    def _generate_improved_search_terms(self, product_data: Dict[str, Any], listing_data: Dict[str, Any]) -> List[str]:
        """
        Genera términos de búsqueda mejorados sin depender de Ollama.
        """
        search_terms = []
        
        # Extraer información básica
        product_name = product_data.get('product_name', '').lower()
        category = product_data.get('category', '').lower()
        features = product_data.get('features', [])
        use_cases = product_data.get('use_cases', [])
        
        # 1. Términos principales específicos del producto
        if product_name:
            # Nombre completo del producto
            search_terms.append(product_name)
            
            # Extraer marca y modelo
            brand, model = self._extract_brand_and_model(product_name)
            if brand:
                search_terms.append(brand)
            if model:
                search_terms.append(f"{brand} {model}" if brand else model)
                
            # Términos específicos por tipo de producto
            specific_terms = self._get_product_specific_terms(product_name, category)
            search_terms.extend(specific_terms)
        
        # 2. Términos de características principales
        for feature in features[:3]:  # Solo las primeras 3 características
            if isinstance(feature, str) and len(feature) > 2:
                search_terms.append(f"{product_name} {feature.lower()}")
        
        # 3. Términos de casos de uso
        for use_case in use_cases[:2]:  # Solo los primeros 2 casos de uso
            if isinstance(use_case, str) and len(use_case) > 2:
                search_terms.append(f"{product_name} {use_case.lower()}")
        
        # 4. Términos de contexto específico
        context_terms = self._get_context_terms(product_name, category)
        search_terms.extend(context_terms)
        
        # 5. Términos para diferentes tipos de imágenes
        image_type_terms = self._get_image_type_terms(product_name)
        search_terms.extend(image_type_terms)
        
        # Limpiar y filtrar términos
        search_terms = self._clean_search_terms(search_terms)
        
        return search_terms[:12]  # Limitar a 12 términos más específicos
    
    def _extract_brand_and_model(self, product_name: str) -> tuple:
        """
        Extrae marca y modelo del nombre del producto.
        """
        # Marcas comunes
        brands = [
            'apple', 'samsung', 'sony', 'lg', 'nike', 'adidas', 'amazon', 'google',
            'microsoft', 'hp', 'dell', 'lenovo', 'asus', 'acer', 'canon', 'nikon',
            'bose', 'jbl', 'beats', 'xiaomi', 'huawei', 'oneplus', 'motorola',
            'fitbit', 'garmin', 'polar', 'casio', 'seiko', 'fossil', 'timex'
        ]
        
        product_lower = product_name.lower()
        found_brand = None
        
        for brand in brands:
            if brand in product_lower:
                found_brand = brand
                break
        
        # Extraer modelo (palabras después de la marca)
        if found_brand:
            # Buscar texto después de la marca
            pattern = rf"{found_brand}\s+(.+?)(?:\s|$)"
            match = re.search(pattern, product_lower)
            if match:
                model = match.group(1).strip()
                return found_brand, model
        
        return found_brand, None
    
    def _get_product_specific_terms(self, product_name: str, category: str) -> List[str]:
        """
        Obtiene términos específicos según el tipo de producto.
        """
        terms = []
        product_lower = product_name.lower()
        category_lower = category.lower()
        
        # Smartwatch/Reloj inteligente
        if any(keyword in product_lower for keyword in ['watch', 'smartwatch', 'reloj']):
            terms.extend([
                f"{product_name} wearable",
                f"{product_name} fitness tracker",
                f"{product_name} smartwatch",
                f"{product_name} wrist device"
            ])
        
        # Sillas
        elif any(keyword in product_lower for keyword in ['chair', 'silla', 'seat']):
            terms.extend([
                f"{product_name} furniture",
                f"{product_name} office chair",
                f"{product_name} gaming chair",
                f"{product_name} ergonomic"
            ])
        
        # Termos y botellas
        elif any(keyword in product_lower for keyword in ['bottle', 'termo', 'flask', 'tumbler']):
            terms.extend([
                f"{product_name} water bottle",
                f"{product_name} insulated bottle",
                f"{product_name} steel bottle",
                f"{product_name} drinkware"
            ])
        
        # Electrónicos
        elif 'electronic' in category_lower or any(keyword in product_lower for keyword in ['device', 'gadget', 'tech']):
            terms.extend([
                f"{product_name} electronic device",
                f"{product_name} gadget",
                f"{product_name} technology"
            ])
        
        # Productos de cocina
        elif 'kitchen' in category_lower or any(keyword in product_lower for keyword in ['kitchen', 'cooking', 'cocina']):
            terms.extend([
                f"{product_name} kitchen appliance",
                f"{product_name} cooking utensil",
                f"{product_name} kitchen gadget"
            ])
        
        return terms
    
    def _get_context_terms(self, product_name: str, category: str) -> List[str]:
        """
        Obtiene términos de contexto para diferentes ambientes de uso.
        """
        terms = []
        product_lower = product_name.lower()
        
        # Contextos según el tipo de producto
        if any(keyword in product_lower for keyword in ['watch', 'fitness', 'sports', 'exercise']):
            terms.extend([
                f"{product_name} lifestyle",
                f"{product_name} active lifestyle",
                f"{product_name} fitness lifestyle"
            ])
        
        elif any(keyword in product_lower for keyword in ['chair', 'desk', 'office', 'work']):
            terms.extend([
                f"{product_name} office setup",
                f"{product_name} workspace",
                f"{product_name} home office"
            ])
        
        elif any(keyword in product_lower for keyword in ['kitchen', 'cooking', 'food', 'drink']):
            terms.extend([
                f"{product_name} kitchen setup",
                f"{product_name} modern kitchen",
                f"{product_name} home cooking"
            ])
        
        return terms
    
    def _get_image_type_terms(self, product_name: str) -> List[str]:
        """
        Obtiene términos para diferentes tipos de imágenes del producto.
        """
        terms = []
        
        # Diferentes perspectivas y tipos de imágenes
        terms.extend([
            f"{product_name} product photography",
            f"{product_name} white background",
            f"{product_name} studio shot",
            f"{product_name} in use",
            f"{product_name} detailed view"
        ])
        
        return terms
    
    def _clean_search_terms(self, terms: List[str]) -> List[str]:
        """
        Limpia y filtra los términos de búsqueda.
        """
        cleaned_terms = []
        
        for term in terms:
            if isinstance(term, str):
                # Limpiar término
                cleaned_term = term.strip().lower()
                cleaned_term = re.sub(r'\s+', ' ', cleaned_term)  # Normalizar espacios
                cleaned_term = re.sub(r'[^\w\s-]', '', cleaned_term)  # Remover caracteres especiales
                
                # Validar término
                if (len(cleaned_term) > 3 and 
                    cleaned_term not in cleaned_terms and 
                    not cleaned_term.startswith('>')):  # Evitar términos de categoría
                    cleaned_terms.append(cleaned_term)
        
        return cleaned_terms
    
    async def _search_images_improved(self, search_terms: List[str], product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca imágenes con mejor relevancia para el producto específico.
        """
        search_results = []
        
        # Usar Pixabay API con consultas mejoradas
        async with aiohttp.ClientSession() as session:
            for term in search_terms:
                try:
                    # Buscar imágenes con el término específico
                    pixabay_results = await self._search_pixabay_improved(session, term, product_data)
                    search_results.extend(pixabay_results)
                    
                    # Añadir pequeña pausa entre consultas
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"Error buscando imágenes para término '{term}': {str(e)}")
                    continue
        
        # Filtrar y ordenar resultados por relevancia
        filtered_results = self._filter_and_rank_results(search_results, product_data)
        
        return filtered_results[:self.max_images]
    
    async def _search_pixabay_improved(self, session: aiohttp.ClientSession, term: str, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca imágenes en Pixabay con parámetros mejorados para relevancia.
        """
        results = []
        
        # Pixabay API key
        api_key = "9656065-a4094594c34f9ac14c7fc4c34f9ac39"
        
        url = "https://pixabay.com/api/"
        
        # Parámetros optimizados para productos
        params = {
            "key": api_key,
            "q": term,
            "image_type": "photo",
            "orientation": "horizontal",
            "category": "backgrounds,science,people,places,animals,industry,food,sports,transportation,travel,buildings,business,music",
            "min_width": 640,
            "min_height": 480,
            "per_page": 6,  # Más imágenes por término
            "safesearch": "true",
            "order": "popular"  # Ordenar por popularidad
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for hit in data.get("hits", []):
                        # Calcular score de relevancia
                        relevance_score = self._calculate_relevance_score(hit, term, product_data)
                        
                        results.append({
                            "url": hit["webformatURL"],
                            "title": f"{term} - {hit.get('tags', '').split(',')[0]}",
                            "description": f"High quality image of {term}",
                            "width": hit["webformatWidth"],
                            "height": hit["webformatHeight"],
                            "search_term": term,
                            "relevance_score": relevance_score,
                            "tags": hit.get("tags", ""),
                            "views": hit.get("views", 0),
                            "downloads": hit.get("downloads", 0),
                            "likes": hit.get("likes", 0)
                        })
                else:
                    logger.warning(f"Pixabay API error for term '{term}': {response.status}")
                    
        except Exception as e:
            logger.warning(f"Error querying Pixabay for term '{term}': {str(e)}")
            
        return results
    
    def _calculate_relevance_score(self, hit: Dict[str, Any], term: str, product_data: Dict[str, Any]) -> float:
        """
        Calcula un score de relevancia para una imagen basado en múltiples factores.
        """
        score = 0.5  # Base score
        
        # Factor 1: Coincidencia de tags
        tags = hit.get("tags", "").lower()
        product_name = product_data.get("product_name", "").lower()
        
        # Boost si el tag contiene el nombre del producto
        if any(word in tags for word in product_name.split()):
            score += 0.3
        
        # Factor 2: Popularidad (views, downloads, likes)
        views = hit.get("views", 0)
        downloads = hit.get("downloads", 0)
        likes = hit.get("likes", 0)
        
        # Normalizar métricas de popularidad
        if views > 1000:
            score += 0.1
        if downloads > 100:
            score += 0.1
        if likes > 10:
            score += 0.1
        
        # Factor 3: Resolución de imagen
        width = hit.get("webformatWidth", 0)
        height = hit.get("webformatHeight", 0)
        
        if width >= 800 and height >= 600:
            score += 0.1
        
        # Factor 4: Coincidencia específica del término
        if term.lower() in tags:
            score += 0.2
        
        return min(1.0, score)
    
    def _filter_and_rank_results(self, results: List[Dict[str, Any]], product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filtra y ordena los resultados por relevancia.
        """
        # Filtrar duplicados por URL
        unique_results = {}
        for result in results:
            url = result.get("url", "")
            if url not in unique_results:
                unique_results[url] = result
        
        # Convertir a lista y ordenar por relevancia
        filtered_results = list(unique_results.values())
        filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return filtered_results
    
    # Métodos heredados del agente original
    async def _download_images(self, image_results: List[Dict[str, Any]], product_name: str) -> List[Dict[str, Any]]:
        """
        Descarga las imágenes encontradas.
        """
        downloaded = []
        safe_product_name = self._sanitize_filename(product_name)
        
        for i, image_data in enumerate(image_results):
            try:
                url = image_data["url"]
                file_extension = self._get_file_extension(url, image_data.get("format", "jpg"))
                
                # Generar nombre único para el archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_product_name}_{timestamp}_{i+1}{file_extension}"
                file_path = os.path.join(self.images_dir, filename)
                
                # Para demo, solo crear registro sin descargar
                downloaded.append({
                    "original_url": url,
                    "local_path": file_path,
                    "filename": filename,
                    "title": image_data.get("title", ""),
                    "search_term": image_data.get("search_term", ""),
                    "width": image_data.get("width", 0),
                    "height": image_data.get("height", 0),
                    "relevance_score": image_data.get("relevance_score", 0),
                    "downloaded_at": datetime.now().isoformat()
                })
                
                # Pequeña pausa
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"No se pudo procesar imagen {i+1}: {str(e)}")
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
            "in_use": [],
            "studio_shots": []
        }
        
        for image in downloaded_images:
            search_term = image.get("search_term", "").lower()
            filename = image.get("filename", "")
            
            if any(word in search_term for word in ["product photography", "white background", "studio"]):
                categories["studio_shots"].append(filename)
            elif any(word in search_term for word in ["lifestyle", "home", "office"]):
                categories["lifestyle"].append(filename)
            elif any(word in search_term for word in ["detail", "close", "view"]):
                categories["detail_shots"].append(filename)
            elif any(word in search_term for word in ["in use", "using", "wearing"]):
                categories["in_use"].append(filename)
            else:
                categories["product_shots"].append(filename)
        
        return categories
    
    def _generate_image_recommendations(self, downloaded_images: List[Dict[str, Any]], listing_data: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones sobre el uso de las imágenes.
        """
        recommendations = []
        
        if len(downloaded_images) == 0:
            recommendations.append("No se encontraron imágenes relevantes. Intenta con términos más específicos.")
            return recommendations
        
        # Evaluar calidad de relevancia
        avg_relevance = sum(img.get("relevance_score", 0) for img in downloaded_images) / len(downloaded_images)
        
        if avg_relevance > 0.8:
            recommendations.append("Excelente relevancia de imágenes encontradas.")
        elif avg_relevance > 0.6:
            recommendations.append("Buena relevancia de imágenes, considera refinar algunos términos.")
        else:
            recommendations.append("Relevancia media, considera usar términos más específicos del producto.")
        
        # Recomendaciones sobre variedad
        if len(downloaded_images) >= 8:
            recommendations.append("Buena variedad de imágenes disponibles.")
        elif len(downloaded_images) >= 5:
            recommendations.append("Variedad adecuada de imágenes.")
        else:
            recommendations.append("Considera buscar más imágenes para mayor variedad.")
        
        # Recomendaciones sobre tipos de imágenes
        has_studio = any("studio" in img.get("search_term", "") for img in downloaded_images)
        has_lifestyle = any("lifestyle" in img.get("search_term", "") for img in downloaded_images)
        
        if not has_studio:
            recommendations.append("Incluye imágenes de producto sobre fondo blanco.")
        if not has_lifestyle:
            recommendations.append("Añade imágenes de estilo de vida mostrando el producto en uso.")
        
        return recommendations[:5]
    
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
        
        if 'content' in previous_results:
            content_result = previous_results['content']
            if isinstance(content_result, dict):
                listing_data.update({
                    'title': content_result.get('title', ''),
                    'description': content_result.get('description', ''),
                    'bullet_points': content_result.get('bullet_points', [])
                })
        
        if 'seo_visual' in previous_results:
            seo_result = previous_results['seo_visual']
            if isinstance(seo_result, dict):
                keywords = seo_result.get('keywords', [])
                if isinstance(keywords, list):
                    listing_data['keywords'].extend(keywords)
        
        return listing_data
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza un nombre de archivo.
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        filename = filename[:50]
        filename = filename.strip()
        
        return filename if filename else "product"
    
    def _get_file_extension(self, url: str, format_hint: str = "") -> str:
        """
        Determina la extensión de archivo.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        for ext in self.supported_formats:
            if path.endswith(ext):
                return ext
        
        if format_hint:
            format_hint = format_hint.lower()
            if format_hint in ['jpg', 'jpeg']:
                return '.jpg'
            elif format_hint in ['png']:
                return '.png'
            elif format_hint in ['webp']:
                return '.webp'
        
        return '.jpg'
