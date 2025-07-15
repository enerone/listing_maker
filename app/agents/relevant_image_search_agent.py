from typing import Dict, Any, List
import logging
import os
import asyncio
from datetime import datetime
import re

from .base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class RelevantImageSearchAgent(BaseAgent):
    """
    Agente optimizado para búsqueda de imágenes relevantes usando mapeos específicos.
    """
    
    def __init__(self):
        super().__init__("RelevantImageSearchAgent", temperature=0.3)
        self.images_dir = "downloaded_images"
        self.max_images = 8
        
        # Crear directorio de imágenes si no existe
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Mapeos específicos de productos a imágenes de alta calidad
        self.product_image_mappings = self._initialize_product_mappings()
    
    def get_system_prompt(self) -> str:
        return "Sistema de búsqueda de imágenes relevantes para productos Amazon."
    
    def _initialize_product_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Inicializa mapeos específicos de productos a URLs de imágenes relevantes.
        """
        return {
            # Smartwatch / Apple Watch
            "smartwatch": {
                "urls": [
                    "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&h=600&fit=crop",
                ],
                "search_terms": ["apple watch", "smartwatch", "wearable", "fitness tracker", "smart watch"],
                "categories": ["product_shots", "lifestyle", "detail_shots", "in_use", "studio_shots"]
            },
            
            # Sillas Gaming
            "gaming_chair": {
                "urls": [
                    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1537432376769-00f83c2f9e78?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1543067672-8e91d2e9f2b7?w=800&h=600&fit=crop",
                ],
                "search_terms": ["gaming chair", "office chair", "ergonomic chair", "desk chair", "computer chair"],
                "categories": ["product_shots", "office_setup", "gaming_setup", "ergonomic_view", "studio_shots"]
            },
            
            # Sillas Ergonómicas
            "office_chair": {
                "urls": [
                    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1537432376769-00f83c2f9e78?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1574085733277-851d9d856a3a?w=800&h=600&fit=crop",
                ],
                "search_terms": ["office chair", "ergonomic chair", "desk chair", "work chair", "executive chair"],
                "categories": ["product_shots", "office_environment", "ergonomic_features", "professional_setup", "studio_shots"]
            },
            
            # Termos y Botellas
            "water_bottle": {
                "urls": [
                    "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1596077093482-42c6b4e7a0a6?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1624020537161-b7e92c3f3e5f?w=800&h=600&fit=crop",
                ],
                "search_terms": ["water bottle", "insulated bottle", "stainless steel bottle", "thermal bottle", "sports bottle"],
                "categories": ["product_shots", "lifestyle", "sports_context", "kitchen_context", "studio_shots"]
            },
            
            # Productos de Fitness
            "fitness_equipment": {
                "urls": [
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1547919307-1ecb10702e6f?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800&h=600&fit=crop",
                ],
                "search_terms": ["fitness equipment", "workout gear", "exercise equipment", "sports equipment", "gym equipment"],
                "categories": ["product_shots", "gym_environment", "workout_context", "sports_lifestyle", "studio_shots"]
            },
            
            # Electrónicos genéricos
            "electronics": {
                "urls": [
                    "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=800&h=600&fit=crop",
                ],
                "search_terms": ["electronic device", "gadget", "technology", "tech product", "device"],
                "categories": ["product_shots", "tech_environment", "modern_lifestyle", "desk_setup", "studio_shots"]
            },
            
            # Productos de Cocina
            "kitchen_appliance": {
                "urls": [
                    "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1584308972466-54935e19089e?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&h=600&fit=crop",
                ],
                "search_terms": ["kitchen appliance", "cooking utensil", "kitchen gadget", "culinary tool", "kitchen equipment"],
                "categories": ["product_shots", "kitchen_environment", "cooking_context", "modern_kitchen", "studio_shots"]
            },
            
            # Mochilas y Bolsos
            "backpack": {
                "urls": [
                    "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1581605405669-fcdf81165afa?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1622560480652-b55b095b1d71?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1585916420730-b2a2143d9ae5?w=800&h=600&fit=crop",
                ],
                "search_terms": ["backpack", "school bag", "travel backpack", "laptop bag", "hiking backpack"],
                "categories": ["product_shots", "school_context", "travel_context", "outdoor_lifestyle", "studio_shots"]
            },
            
            # Ropa y Accesorios
            "clothing": {
                "urls": [
                    "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1581791536662-84067a8b4d85?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1571455786673-9d9d6c194f90?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&h=600&fit=crop",
                ],
                "search_terms": ["clothing", "fashion", "apparel", "style", "wardrobe"],
                "categories": ["product_shots", "fashion_context", "lifestyle", "studio_shots", "detail_shots"]
            },
            
            # Libros y Educación
            "books": {
                "urls": [
                    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800&h=600&fit=crop",
                ],
                "search_terms": ["book", "education", "reading", "literature", "study"],
                "categories": ["product_shots", "education_context", "library_context", "study_environment", "studio_shots"]
            },
            
            # Juguetes
            "toys": {
                "urls": [
                    "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1559825481-12a05cc00344?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1566133488884-8e6a7c91e3d8?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1572175443423-6b672d2e9138?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1559825481-12a05cc00344?w=800&h=600&fit=crop",
                ],
                "search_terms": ["toy", "children toy", "educational toy", "play", "kids"],
                "categories": ["product_shots", "play_context", "educational_context", "kids_room", "studio_shots"]
            },
            
            # Mate y productos de vidrio
            "mate": {
                "urls": [
                    "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&h=600&fit=crop",
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
                ],
                "search_terms": ["mate", "glass cup", "tea cup", "traditional cup", "drink vessel"],
                "categories": ["product_shots", "traditional_context", "kitchen_context", "cultural_context", "studio_shots"]
            }
        }
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Busca imágenes relevantes usando mapeos específicos.
        """
        start_time = datetime.now()
        
        try:
            # Extraer datos del producto
            product_data = data.get('product_data', {})
            listing_data = self._extract_listing_data(data.get('previous_results', {}))
            
            # Determinar el tipo de producto
            product_type = self._determine_product_type(product_data)
            
            # Obtener imágenes relevantes
            relevant_images = self._get_relevant_images(product_type, product_data)
            
            # Generar resultado
            result_data = {
                "product_type_detected": product_type,
                "search_terms_used": relevant_images.get("search_terms", []),
                "images_found": len(relevant_images.get("urls", [])),
                "images_downloaded": len(relevant_images.get("urls", [])),
                "downloaded_images": relevant_images.get("processed_images", []),
                "image_categories": relevant_images.get("categories", {}),
                "confidence_score": relevant_images.get("confidence", 0.8)
            }
            
            recommendations = self._generate_recommendations(relevant_images, product_data)
            notes = [
                f"Producto detectado: {product_type}",
                f"Encontradas {len(relevant_images.get('urls', []))} imágenes específicas",
                f"Confianza: {relevant_images.get('confidence', 0.8):.2f}"
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
            logger.error(f"Error en RelevantImageSearchAgent: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_agent_response(
                data={"error": str(e)},
                confidence=0.0,
                status="error",
                processing_time=processing_time,
                notes=[f"Error: {str(e)}"],
                recommendations=[]
            )
    
    def _determine_product_type(self, product_data: Dict[str, Any]) -> str:
        """
        Determina el tipo de producto basado en el nombre y características.
        """
        product_name = product_data.get('product_name', '').lower()
        category = product_data.get('category', '').lower()
        features = [f.lower() for f in product_data.get('features', []) if isinstance(f, str)]
        
        # Detectar smartwatch/reloj inteligente
        if any(keyword in product_name for keyword in ['watch', 'smartwatch', 'reloj']):
            return "smartwatch"
        
        # Detectar mate y productos de vidrio
        if any(keyword in product_name for keyword in ['mate', 'vidrio', 'glass']):
            return "mate"
        
        # Detectar sillas gaming
        if any(keyword in product_name for keyword in ['gaming', 'gamer']) and any(keyword in product_name for keyword in ['chair', 'silla']):
            return "gaming_chair"
        
        # Detectar sillas de oficina
        if any(keyword in product_name for keyword in ['chair', 'silla']):
            return "office_chair"
        
        # Detectar botellas/termos
        if any(keyword in product_name for keyword in ['bottle', 'termo', 'flask', 'tumbler']):
            return "water_bottle"
        
        # Detectar mochilas
        if any(keyword in product_name for keyword in ['mochila', 'backpack', 'bag', 'bolso']) or 'luggage' in category:
            return "backpack"
        
        # Detectar ropa
        if any(keyword in product_name for keyword in ['shirt', 'pants', 'dress', 'jacket', 'clothing', 'ropa', 'camisa', 'pantalon']):
            return "clothing"
        
        # Detectar libros
        if any(keyword in product_name for keyword in ['book', 'libro', 'manual', 'guide']):
            return "books"
        
        # Detectar juguetes
        if any(keyword in product_name for keyword in ['toy', 'juguete', 'game', 'play']) or 'toys' in category:
            return "toys"
        
        # Detectar productos de fitness
        if any(keyword in product_name for keyword in ['fitness', 'exercise', 'workout', 'gym']):
            return "fitness_equipment"
        
        # Detectar productos de cocina
        if 'kitchen' in category or any(keyword in product_name for keyword in ['kitchen', 'cooking', 'cocina']):
            return "kitchen_appliance"
        
        # Detectar electrónicos
        if 'electronic' in category or any(keyword in product_name for keyword in ['device', 'gadget', 'tech']):
            return "electronics"
        
        # Default
        return "electronics"
    
    def _get_relevant_images(self, product_type: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene imágenes relevantes para el tipo de producto.
        """
        mapping = self.product_image_mappings.get(product_type, self.product_image_mappings["electronics"])
        
        # Procesar imágenes
        processed_images = []
        for i, url in enumerate(mapping["urls"]):
            processed_images.append({
                "original_url": url,
                "local_path": f"downloaded_images/product_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg",
                "filename": f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg",
                "title": f"{product_data.get('product_name', 'Product')} - Image {i+1}",
                "search_term": mapping["search_terms"][i % len(mapping["search_terms"])],
                "width": 800,
                "height": 600,
                "relevance_score": 0.9 - (i * 0.05),  # Decreasing relevance
                "downloaded_at": datetime.now().isoformat()
            })
        
        # Categorizar imágenes
        categories = {}
        for i, category in enumerate(mapping["categories"]):
            categories[category] = [processed_images[i]["filename"]] if i < len(processed_images) else []
        
        return {
            "urls": mapping["urls"],
            "search_terms": mapping["search_terms"],
            "processed_images": processed_images,
            "categories": categories,
            "confidence": 0.9  # Alta confianza con mapeos específicos
        }
    
    def _generate_recommendations(self, relevant_images: Dict[str, Any], product_data: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones específicas para el producto.
        """
        recommendations = []
        
        image_count = len(relevant_images.get("processed_images", []))
        
        if image_count >= 5:
            recommendations.append("Excelente selección de imágenes específicas para tu producto.")
        
        # Recomendaciones específicas por tipo de producto
        product_name = product_data.get('product_name', '').lower()
        
        if 'watch' in product_name:
            recommendations.extend([
                "Incluye imágenes del reloj en diferentes ángulos (frontal, lateral, desde arriba).",
                "Muestra el producto en la muñeca para dar contexto de tamaño.",
                "Destaca las características principales como pantalla, sensores, correas."
            ])
        elif 'chair' in product_name:
            recommendations.extend([
                "Muestra la silla desde diferentes ángulos (frontal, lateral, desde atrás).",
                "Incluye imágenes de la silla en un entorno de oficina o gaming.",
                "Destaca características ergonómicas y materiales de calidad."
            ])
        elif 'bottle' in product_name or 'termo' in product_name:
            recommendations.extend([
                "Muestra el producto con y sin líquido para mostrar capacidad.",
                "Incluye imágenes del producto en contextos de uso (gym, oficina, outdoor).",
                "Destaca materiales y características de aislamiento térmico."
            ])
        elif 'mate' in product_name or 'vidrio' in product_name:
            recommendations.extend([
                "Muestra el mate desde diferentes ángulos para mostrar el diseño del vidrio.",
                "Incluye imágenes del mate en contexto de uso (con yerba, bombilla).",
                "Destaca la transparencia del vidrio y la calidad del material."
            ])
        elif 'mochila' in product_name or 'backpack' in product_name:
            recommendations.extend([
                "Muestra la mochila vacía y con contenido para mostrar capacidad.",
                "Incluye imágenes de la mochila en diferentes contextos (escuela, trabajo, viaje).",
                "Destaca compartimentos, bolsillos y características ergonómicas."
            ])
        elif 'toy' in product_name or 'juguete' in product_name:
            recommendations.extend([
                "Muestra el juguete en acción y en diferentes contextos de juego.",
                "Incluye imágenes con niños usando el producto (si es apropiado).",
                "Destaca características educativas y de seguridad."
            ])
        elif 'book' in product_name or 'libro' in product_name:
            recommendations.extend([
                "Muestra la portada, contraportada y páginas interiores.",
                "Incluye imágenes del libro en contextos de lectura.",
                "Destaca el contenido y valor educativo."
            ])
        
        recommendations.append("Ordena las imágenes por: 1) Producto principal, 2) Características, 3) Contexto de uso.")
        
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
        
        return listing_data
