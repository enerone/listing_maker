"""
Servicio de integración con Stockimg.ai para generación de imágenes
Con fallback a servicios alternativos
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class StockimgService:
    """
    Servicio para generar imágenes usando la API de Stockimg.ai con fallbacks
    """
    
    def __init__(self):
        # API de Stockimg.ai
        self.api_key = "ErPtrkevzEK2w4x4ctp6fmSTzxjN4IDtKcaMXKg9PjV6e9vtimSHRJOiL8bauyFS" 
        self.images_dir = "stockimg_generated"
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Importar el servicio híbrido como fallback
        try:
            from .hybrid_image_service import get_hybrid_image_service
            self.hybrid_service = get_hybrid_image_service()
            logger.info("✅ Servicio híbrido cargado correctamente")
        except Exception as e:
            self.hybrid_service = None
            logger.warning(f"⚠️ Servicio híbrido no disponible: {str(e)}")
        
        logger.info(f"🎨 StockimgService inicializado - Directorio: {self.images_dir}")
    
    async def generate_image(
        self, 
        prompt: str, 
        style: str = "product_photography",
        width: int = 1024,
        height: int = 1024
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una imagen usando Stockimg.ai
        
        Args:
            prompt: Prompt para generar la imagen
            style: Estilo de imagen (product_photography, lifestyle, etc.)
            width: Ancho de la imagen
            height: Alto de la imagen
            
        Returns:
            Diccionario con información de la imagen generada o None si hay error
        """
        try:
            logger.info(f"🎨 Generando imagen con Stockimg.ai - Prompt: {prompt[:100]}...")
            
            # Saltamos la verificación por ahora debido a Cloudflare
            logger.info("ℹ️ Saltando verificación de API key debido a protección Cloudflare")
            
            # Primero intentar con Stockimg.ai directamente (implementación simplificada)
            result = await self._try_stockimg_direct(prompt, style, width, height)
            if result:
                return result
            
            # Si Stockimg.ai falla, usar el servicio híbrido como fallback
            if self.hybrid_service:
                logger.info("🔄 Stockimg.ai falló, usando servicio híbrido como fallback...")
                return await self.hybrid_service.generate_image(
                    prompt=prompt,
                    style=style,
                    width=width,
                    height=height,
                    preferred_service="stability"  # Usar Stability AI como fallback principal
                )
            else:
                logger.error("❌ No hay servicios de fallback disponibles")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generando imagen con Stockimg.ai: {str(e)}")
            return None
    
    async def _try_stockimg_direct(
        self, 
        prompt: str, 
        style: str, 
        width: int, 
        height: int
    ) -> Optional[Dict[str, Any]]:
        """
        Intenta generar imagen directamente con Stockimg.ai (versión simplificada)
        """
        try:
            # URLs base a probar
            base_urls = [
                "https://api.stockimg.ai",
                "https://stockimg.ai/api"
            ]
            # Preparar headers simplificados
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "StockimgAI-Client/1.0"
            }
            
            # Payload simplificado
            payload = {
                "prompt": prompt,
                "style": self._map_style_to_stockimg(style),
                "width": width,
                "height": height
            }
            
            # Hacer petición simplificada a Stockimg.ai
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Intentar solo los endpoints más prometedores
                endpoints = ["/v1/generate", "/generate"]
                
                for base_url in base_urls:
                    for endpoint in endpoints:
                        try:
                            url = f"{base_url}{endpoint}"
                            logger.info(f"🔄 Probando: {url}")
                            
                            response = await client.post(url, headers=headers, json=payload)
                            
                            if response.status_code == 200:
                                result = response.json()
                                logger.info(f"✅ Respuesta exitosa de Stockimg.ai: {result}")
                                
                                # Extraer URL de imagen
                                image_url = (result.get("image_url") or 
                                           result.get("url") or 
                                           result.get("output_url"))
                                
                                if image_url:
                                    return await self._download_and_save_image(
                                        image_url, prompt, style
                                    )
                            else:
                                logger.debug(f"❌ Error {response.status_code} en {url}")
                                
                        except Exception as e:
                            logger.debug(f"Error en {url}: {str(e)}")
                            continue
            
            logger.warning("⚠️ No se pudo conectar con Stockimg.ai")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error intentando Stockimg.ai directo: {str(e)}")
            return None
    
    def _map_style_to_stockimg(self, style: str) -> str:
        """
        Mapea nuestros estilos internos a los estilos de Stockimg.ai
        """
        style_mapping = {
            "main_product": "product-photography",
            "product_photography": "product-photography",
            "contextual": "lifestyle",
            "lifestyle": "lifestyle",
            "detail": "macro",
            "comparative": "infographic",
            "technical": "technical-drawing"
        }
        
        return style_mapping.get(style, "product-photography")
    
    async def _download_and_save_image(
        self, 
        image_url: str, 
        prompt: str, 
        style: str
    ) -> Optional[Dict[str, Any]]:
        """
        Descarga y guarda una imagen desde la URL proporcionada por Stockimg.ai
        """
        try:
            if not image_url:
                logger.error("❌ URL de imagen no proporcionada")
                return None
                
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"stockimg_{style}_{timestamp}_{unique_id}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            # Descargar imagen
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                
                if response.status_code == 200:
                    # Guardar archivo
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    # Obtener información del archivo
                    file_size = os.path.getsize(filepath)
                    
                    return {
                        "filename": filename,
                        "filepath": filepath,
                        "url": f"/stockimg_generated/{filename}",
                        "prompt": prompt,
                        "style": style,
                        "width": 1024,  # Stockimg.ai default
                        "height": 1024,
                        "file_size": file_size,
                        "generated_at": datetime.now().isoformat(),
                        "service": "stockimg.ai"
                    }
                else:
                    logger.error(f"❌ Error descargando imagen: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error descargando imagen: {str(e)}")
            return None
    
    async def generate_images_from_prompts(
        self, 
        prompts: Dict[str, str],
        product_name: str
    ) -> List[Dict[str, Any]]:
        """
        Genera múltiples imágenes desde un diccionario de prompts
        
        Args:
            prompts: Diccionario con prompts {tipo: prompt}
            product_name: Nombre del producto para logging
            
        Returns:
            Lista de diccionarios con información de las imágenes generadas
        """
        try:
            logger.info(f"🎨 Generando {len(prompts)} imágenes para: {product_name}")
            
            generated_images = []
            
            for prompt_type, prompt_text in prompts.items():
                if not prompt_text or not prompt_text.strip():
                    logger.warning(f"⚠️ Prompt vacío para tipo: {prompt_type}")
                    continue
                
                try:
                    # Generar imagen individual
                    image_info = await self.generate_image(
                        prompt=prompt_text,
                        style=prompt_type
                    )
                    
                    if image_info:
                        image_info['prompt_type'] = prompt_type
                        image_info['product_name'] = product_name
                        generated_images.append(image_info)
                        
                        # Esperar un poco entre generaciones para no sobrecargar la API
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    logger.error(f"❌ Error generando imagen {prompt_type}: {str(e)}")
                    continue
            
            logger.info(f"✅ Generadas {len(generated_images)} imágenes con Stockimg.ai")
            return generated_images
            
        except Exception as e:
            logger.error(f"❌ Error en generación múltiple: {str(e)}")
            return []
    
    def get_generated_images_info(self) -> List[Dict[str, Any]]:
        """
        Obtiene información de todas las imágenes generadas por Stockimg.ai
        """
        images_info = []
        
        if not os.path.exists(self.images_dir):
            return images_info
        
        for filename in os.listdir(self.images_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(self.images_dir, filename)
                try:
                    # Obtener info básica del archivo
                    stat = os.stat(filepath)
                    images_info.append({
                        "filename": filename,
                        "filepath": filepath,
                        "url": f"/stockimg_generated/{filename}",
                        "file_size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "service": "stockimg.ai"
                    })
                except Exception as e:
                    logger.error(f"Error obteniendo info de {filename}: {str(e)}")
                    continue
        
        # Ordenar por fecha de creación (más recientes primero)
        images_info.sort(key=lambda x: x["created_at"], reverse=True)
        return images_info
    
    def cleanup_old_images(self, max_images: int = 50):
        """
        Limpia imágenes antiguas para mantener el storage bajo control
        """
        try:
            images_info = self.get_generated_images_info()
            
            if len(images_info) > max_images:
                # Eliminar imágenes más antiguas
                to_delete = images_info[max_images:]
                
                for image_info in to_delete:
                    try:
                        os.remove(image_info["filepath"])
                        logger.info(f"🗑️ Imagen Stockimg antigua eliminada: {image_info['filename']}")
                    except Exception as e:
                        logger.error(f"Error eliminando {image_info['filename']}: {str(e)}")
                
                logger.info(f"🧹 Limpieza Stockimg completada: {len(to_delete)} imágenes eliminadas")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de imágenes Stockimg: {str(e)}")
    
    async def verify_api_key(self) -> bool:
        """
        Verifica si la API key es válida haciendo una petición simple
        """
        try:
            logger.info("🔍 Verificando validez de API key de Stockimg.ai...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Probar diferentes endpoints de verificación
                test_endpoints = [
                    ("https://stockimg.ai/api/user", {"Authorization": f"Bearer {self.api_key}"}),
                    ("https://api.stockimg.ai/user", {"Authorization": f"Bearer {self.api_key}"}),
                    ("https://stockimg.ai/api/v1/user", {"X-API-Key": self.api_key}),
                    ("https://api.stockimg.ai/v1/user", {"X-API-Key": self.api_key}),
                ]
                
                for url, headers in test_endpoints:
                    try:
                        logger.info(f"🔍 Probando verificación en: {url}")
                        response = await client.get(url, headers=headers)
                        logger.info(f"📡 Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            logger.info("✅ API key válida!")
                            return True
                        elif response.status_code in [401, 403]:
                            error_text = response.text[:300]
                            logger.error(f"❌ API key inválida en {url}: {error_text}")
                        else:
                            logger.info(f"ℹ️ Endpoint {url} devolvió: {response.status_code}")
                            
                    except Exception as e:
                        logger.debug(f"Error verificando {url}: {str(e)}")
                        continue
                
                logger.error("❌ No se pudo verificar la validez de la API key")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando API key: {str(e)}")
            return False


# Instancia global del servicio
_stockimg_service = None

def get_stockimg_service() -> StockimgService:
    """
    Obtiene la instancia global del servicio de Stockimg.ai
    """
    global _stockimg_service
    if _stockimg_service is None:
        _stockimg_service = StockimgService()
    return _stockimg_service
