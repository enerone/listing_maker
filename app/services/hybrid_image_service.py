"""
Servicio híbrido de generación de imágenes que integra múltiples APIs
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class HybridImageService:
    """
    Servicio híbrido que puede usar Stockimg.ai, OpenAI DALL-E, y otras APIs
    """
    
    def __init__(self):
        # APIs disponibles
        self.stockimg_api_key = "ErPtrkevzEK2w4x4ctp6fmSTzxjN4IDtKcaMXKg9PjV6e9vtimSHRJOiL8bauyFS"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        
        self.images_dir = "generated_images"
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Log de configuración
        has_openai = bool(self.openai_api_key)
        has_stability = bool(self.stability_api_key)
        logger.info(f"🎨 HybridImageService inicializado - Directorio: {self.images_dir}")
        logger.info(f"🔑 OpenAI API disponible: {has_openai}")
        logger.info(f"🔑 Stability AI disponible: {has_stability}")
        if has_openai and self.openai_api_key:
            logger.info(f"🔑 OpenAI API key (últimos 4 chars): ...{self.openai_api_key[-4:]}")
        if has_stability and self.stability_api_key:
            logger.info(f"🔑 Stability API key (últimos 4 chars): ...{self.stability_api_key[-4:]}")
    
    async def generate_image(
        self, 
        prompt: str, 
        style: str = "product_photography",
        width: int = 1024,
        height: int = 1024,
        preferred_service: str = "auto"
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una imagen usando el mejor servicio disponible
        
        Args:
            prompt: Prompt para generar la imagen
            style: Estilo de imagen
            width: Ancho de la imagen
            height: Alto de la imagen
            preferred_service: "stockimg", "openai", "auto"
            
        Returns:
            Diccionario con información de la imagen generada
        """
        try:
            logger.info(f"🎨 Generando imagen híbrida - Prompt: {prompt[:100]}...")
            
            # Intentar servicios en orden de preferencia
            services_to_try = []
            
            if preferred_service == "stockimg":
                services_to_try = ["stockimg", "stability", "openai", "free_sd"]
            elif preferred_service == "openai":
                services_to_try = ["openai", "stability", "stockimg", "free_sd"]
            elif preferred_service == "stability":
                services_to_try = ["stability", "stockimg", "openai", "free_sd"]
            else:  # auto
                services_to_try = ["stockimg", "stability", "free_sd", "openai"]
            
            for service in services_to_try:
                try:
                    if service == "stockimg":
                        result = await self._generate_with_stockimg(prompt, style, width, height)
                        if result:
                            return result
                        logger.warning("⚠️ Stockimg.ai falló, probando siguiente servicio...")
                        
                    elif service == "openai" and self.openai_api_key:
                        result = await self._generate_with_openai(prompt, style, width, height)
                        if result:
                            return result
                        logger.warning("⚠️ OpenAI falló, probando siguiente servicio...")
                        
                    elif service == "stability" and self.stability_api_key:
                        result = await self._generate_with_stability(prompt, style, width, height)
                        if result:
                            return result
                        logger.warning("⚠️ Stability AI falló, probando siguiente servicio...")
                        
                    elif service == "free_sd":
                        result = await self._generate_with_free_sd(prompt, style, width, height)
                        if result:
                            return result
                        logger.warning("⚠️ Stable Diffusion gratuito falló, probando siguiente servicio...")
                        
                except Exception as e:
                    logger.error(f"❌ Error con {service}: {str(e)}")
                    continue
            
            logger.error("❌ Todos los servicios de generación de imágenes fallaron")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en generación híbrida: {str(e)}")
            return None
    
    async def _generate_with_stockimg(
        self, 
        prompt: str, 
        style: str, 
        width: int, 
        height: int
    ) -> Optional[Dict[str, Any]]:
        """
        Intenta generar con Stockimg.ai (implementación simplificada)
        """
        try:
            logger.info("🔄 Intentando con Stockimg.ai...")
            
            # Implementación simplificada que evita Cloudflare
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Probar solo los endpoints más prometedores
                endpoints = [
                    "https://api.stockimg.ai/v1/generate",
                    "https://stockimg.ai/api/generate"
                ]
                
                for endpoint in endpoints:
                    try:
                        headers = {
                            "Authorization": f"Bearer {self.stockimg_api_key}",
                            "Content-Type": "application/json",
                            "User-Agent": "StockimgAI-Client/1.0"
                        }
                        
                        payload = {
                            "prompt": prompt,
                            "style": self._map_style_to_stockimg(style),
                            "width": width,
                            "height": height
                        }
                        
                        response = await client.post(endpoint, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            result = response.json()
                            image_url = result.get("image_url") or result.get("url")
                            
                            if image_url:
                                return await self._download_and_save_image(
                                    image_url, prompt, style, "stockimg.ai"
                                )
                        
                    except Exception as e:
                        logger.debug(f"Error en {endpoint}: {str(e)}")
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error con Stockimg.ai: {str(e)}")
            return None
    
    async def _generate_with_openai(
        self, 
        prompt: str, 
        style: str, 
        width: int, 
        height: int
    ) -> Optional[Dict[str, Any]]:
        """
        Genera imagen usando OpenAI DALL-E
        """
        try:
            if not self.openai_api_key:
                logger.warning("⚠️ OpenAI API key no configurada")
                return None
                
            logger.info("🔄 Intentando con OpenAI DALL-E...")
            
            # Ajustar prompt para DALL-E
            dall_e_prompt = self._adapt_prompt_for_dalle(prompt, style)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Usar DALL-E 3 para mejor calidad
                payload = {
                    "model": "dall-e-3",
                    "prompt": dall_e_prompt,
                    "size": f"{width}x{height}" if f"{width}x{height}" in ["1024x1024", "1024x1792", "1792x1024"] else "1024x1024",
                    "quality": "hd",
                    "n": 1
                }
                
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_data = result.get("data", [])
                    
                    if image_data and len(image_data) > 0:
                        image_url = image_data[0].get("url")
                        if image_url:
                            return await self._download_and_save_image(
                                image_url, prompt, style, "openai-dalle"
                            )
                else:
                    error_text = response.text[:200]
                    logger.error(f"❌ Error OpenAI: {response.status_code} - {error_text}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error con OpenAI: {str(e)}")
            return None
    
    async def _generate_with_stability(
        self, 
        prompt: str, 
        style: str, 
        width: int, 
        height: int
    ) -> Optional[Dict[str, Any]]:
        """
        Genera imagen usando Stability AI (Stable Diffusion)
        """
        try:
            if not self.stability_api_key:
                logger.warning("⚠️ Stability AI API key no configurada")
                return None
                
            logger.info("🔄 Intentando con Stability AI (Stable Diffusion)...")
            
            # Adaptar prompt para Stable Diffusion
            stability_prompt = self._adapt_prompt_for_stability(prompt, style)
            
            # Asegurar dimensiones válidas para Stable Diffusion
            valid_sizes = [(512, 512), (768, 768), (1024, 1024), (512, 768), (768, 512)]
            closest_size = min(valid_sizes, key=lambda x: abs(x[0] - width) + abs(x[1] - height))
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.stability_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Payload para Stability AI API
                payload = {
                    "text_prompts": [
                        {
                            "text": stability_prompt,
                            "weight": 1.0
                        }
                    ],
                    "cfg_scale": 7,
                    "height": closest_size[1],
                    "width": closest_size[0],
                    "samples": 1,
                    "steps": 30,
                    "style_preset": self._get_stability_style(style)
                }
                
                # Usar SDXL 1.0 que es el modelo más reciente
                url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
                
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    artifacts = result.get("artifacts", [])
                    
                    if artifacts and len(artifacts) > 0:
                        # Stability AI devuelve la imagen en base64
                        image_data = artifacts[0].get("base64")
                        if image_data:
                            return await self._save_base64_image(
                                image_data, prompt, style, "stability-ai"
                            )
                else:
                    error_text = response.text[:200]
                    logger.error(f"❌ Error Stability AI: {response.status_code} - {error_text}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error con Stability AI: {str(e)}")
            return None
    
    def _adapt_prompt_for_dalle(self, prompt: str, style: str) -> str:
        """
        Adapta el prompt para DALL-E según el estilo
        """
        style_prefixes = {
            "product_photography": "Professional product photography of",
            "main_product": "High-quality studio photography of",
            "lifestyle": "Lifestyle photography featuring",
            "contextual": "Real-world setting showing",
            "detail": "Detailed close-up photography of",
            "technical": "Technical illustration of"
        }
        
        prefix = style_prefixes.get(style, "Professional photography of")
        return f"{prefix} {prompt}, high quality, professional lighting, clean background"
    
    def _map_style_to_stockimg(self, style: str) -> str:
        """
        Mapea estilos para Stockimg.ai
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
    
    def _adapt_prompt_for_stability(self, prompt: str, style: str) -> str:
        """
        Adapta el prompt para Stable Diffusion según el estilo
        """
        style_suffixes = {
            "product_photography": ", professional product photography, studio lighting, white background, high resolution, commercial quality",
            "main_product": ", product shot, clean background, professional lighting, marketing photo, high quality",
            "lifestyle": ", lifestyle photography, natural lighting, real-world context, candid",
            "contextual": ", in use, real environment, natural setting, practical context",
            "detail": ", macro photography, close-up, detailed, sharp focus, high resolution",
            "technical": ", technical diagram, clean lines, informative, precise"
        }
        
        suffix = style_suffixes.get(style, ", professional photography, high quality")
        return f"{prompt}{suffix}"
    
    def _get_stability_style(self, style: str) -> str:
        """
        Mapea estilos a presets de Stability AI
        """
        style_mapping = {
            "product_photography": "photographic",
            "main_product": "photographic", 
            "lifestyle": "photographic",
            "contextual": "photographic",
            "detail": "photographic",
            "technical": "digital-art"
        }
        
        return style_mapping.get(style, "photographic")
    
    async def _download_and_save_image(
        self, 
        image_url: str, 
        prompt: str, 
        style: str,
        service: str
    ) -> Optional[Dict[str, Any]]:
        """
        Descarga y guarda una imagen
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{service}_{style}_{timestamp}_{unique_id}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    file_size = os.path.getsize(filepath)
                    
                    return {
                        "filename": filename,
                        "filepath": filepath,
                        "url": f"/generated_images/{filename}",
                        "prompt": prompt,
                        "style": style,
                        "width": 1024,
                        "height": 1024,
                        "file_size": file_size,
                        "generated_at": datetime.now().isoformat(),
                        "service": service
                    }
                else:
                    logger.error(f"❌ Error descargando imagen: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error descargando imagen: {str(e)}")
            return None
    
    async def _save_base64_image(
        self, 
        base64_data: str, 
        prompt: str, 
        style: str, 
        service: str
    ) -> Optional[Dict[str, Any]]:
        """
        Guarda una imagen desde datos base64 (para Stability AI)
        """
        try:
            import base64
            
            # Decodificar base64
            image_bytes = base64.b64decode(base64_data)
            
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{service}_{style}_{timestamp}_{unique_id}.png"
            filepath = os.path.join(self.images_dir, filename)
            
            # Guardar archivo
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            # Obtener información del archivo
            file_size = os.path.getsize(filepath)
            
            return {
                "filename": filename,
                "filepath": filepath,
                "url": f"/generated_images/{filename}",
                "prompt": prompt,
                "style": style,
                "width": 1024,  # Estándar para Stability AI
                "height": 1024,
                "file_size": file_size,
                "generated_at": datetime.now().isoformat(),
                "service": service
            }
            
        except Exception as e:
            logger.error(f"❌ Error guardando imagen base64: {str(e)}")
            return None
    
    async def _generate_with_free_sd(
        self, 
        prompt: str, 
        style: str, 
        width: int, 
        height: int
    ) -> Optional[Dict[str, Any]]:
        """
        Genera imagen usando Stable Diffusion gratuito (Hugging Face)
        """
        try:
            logger.info("🆓 Intentando con Stable Diffusion gratuito (Hugging Face)...")
            
            # Importar el servicio gratuito
            from .free_stable_diffusion_service import get_free_stable_diffusion_service
            free_service = get_free_stable_diffusion_service()
            
            # Generar imagen
            result = await free_service.generate_image(prompt, style, width, height)
            return result
            
        except Exception as e:
            logger.error(f"❌ Error con Stable Diffusion gratuito: {str(e)}")
            return None


# Instancia global del servicio
_hybrid_service = None

def get_hybrid_image_service() -> HybridImageService:
    """
    Obtiene la instancia global del servicio híbrido de imágenes
    """
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridImageService()
    return _hybrid_service
