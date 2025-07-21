"""
Servicio de integración con Stockimg.ai para generación de imágenes
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
    Servicio para generar imágenes usando la API de Stockimg.ai
    """
    
    def __init__(self):
        self.api_key = "OsM9sVIWDAD8m7EZXL4CWBGzzeKxbCCvK4wc4Vw6IbPwpT5PcyBOLMbBMWApvOmF"
        self.base_url = "https://api.stockimg.ai"
        self.images_dir = "stockimg_generated"
        
        # Crear directorio de imágenes si no existe
        os.makedirs(self.images_dir, exist_ok=True)
        
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
            
            # Preparar headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Mapear estilos internos a estilos de Stockimg.ai
            stockimg_style = self._map_style_to_stockimg(style)
            
            # Preparar payload para la API
            payload = {
                "prompt": prompt,
                "style": stockimg_style,
                "width": width,
                "height": height,
                "format": "jpeg",
                "quality": "high"
            }
            
            # Hacer petición a la API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/generate",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Descargar y guardar la imagen
                    image_info = await self._download_and_save_image(
                        result.get("image_url"),
                        prompt,
                        style
                    )
                    
                    if image_info:
                        logger.info(f"✅ Imagen generada exitosamente: {image_info['filename']}")
                        return image_info
                    else:
                        logger.error("❌ Error descargando imagen generada")
                        return None
                        
                else:
                    logger.error(f"❌ Error en API Stockimg.ai: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error generando imagen con Stockimg.ai: {str(e)}")
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
