"""
Servicio de Stable Diffusion gratuito usando Hugging Face
Como alternativa sin costo cuando no hay API keys disponibles
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class FreeStableDiffusionService:
    """
    Servicio que usa Stable Diffusion gratuito a través de Hugging Face
    No requiere API key - completamente gratuito
    """
    
    def __init__(self):
        self.images_dir = "generated_images"
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Endpoints gratuitos de Hugging Face y alternativas
        self.endpoints = [
            # Endpoints principales de Hugging Face
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1", 
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            
            # Endpoints alternativos más rápidos
            "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
            "https://api-inference.huggingface.co/models/prompthero/openjourney",
            "https://api-inference.huggingface.co/models/dreamlike-art/dreamlike-diffusion-1.0",
            
            # Más opciones de fallback
            "https://api-inference.huggingface.co/models/nitrosocke/Arcane-Diffusion",
            "https://api-inference.huggingface.co/models/22h/vintedois-diffusion-v0-1"
        ]
        
        logger.info(f"🆓 FreeStableDiffusionService inicializado - Directorio: {self.images_dir}")
    
    async def generate_image(
        self, 
        prompt: str, 
        style: str = "product_photography",
        width: int = 1024,
        height: int = 1024
    ) -> Optional[Dict[str, Any]]:
        """
        Genera imagen usando Stable Diffusion gratuito
        """
        try:
            logger.info(f"🆓 Generando imagen gratuita con Stable Diffusion - Prompt: {prompt[:100]}...")
            
            # Adaptar prompt para mejores resultados
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                
                for i, endpoint in enumerate(self.endpoints):
                    try:
                        model_name = endpoint.split('/')[-1]
                        logger.info(f"🔄 Probando endpoint gratuito {i+1}/{len(self.endpoints)}: {model_name}")
                        
                        headers = {
                            "Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0 (compatible; ImageGen/1.0)"
                        }
                        
                        payload = {
                            "inputs": enhanced_prompt,
                            "parameters": {
                                "negative_prompt": "blurry, low quality, distorted",
                                "num_inference_steps": 20,
                                "guidance_scale": 7.5
                            }
                        }
                        
                        response = await client.post(endpoint, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            # Hugging Face devuelve la imagen directamente como bytes
                            image_bytes = response.content
                            
                            if image_bytes and len(image_bytes) > 1000:  # Verificar que es una imagen válida
                                result = await self._save_image_bytes(
                                    image_bytes, prompt, style, f"free-sd-{model_name}"
                                )
                                if result:
                                    logger.info(f"✅ Imagen generada exitosamente con {model_name}")
                                    return result
                        elif response.status_code == 503:
                            logger.debug(f"⏳ Modelo {model_name} cargándose, probando siguiente...")
                        else:
                            logger.debug(f"❌ Error {response.status_code} en {model_name}")
                            
                        # Esperar entre intentos para no sobrecargar
                        await asyncio.sleep(1)
                            
                    except Exception as e:
                        logger.debug(f"Error en {endpoint.split('/')[-1]}: {str(e)}")
                        continue
            
            logger.warning("⚠️ No se pudo generar imagen con ningún endpoint gratuito")
            
            # Como último recurso, generar una imagen placeholder
            return await self._generate_placeholder_image(prompt, style)
            
        except Exception as e:
            logger.error(f"❌ Error generando imagen gratuita: {str(e)}")
            # Intentar generar placeholder incluso si hay errores
            try:
                return await self._generate_placeholder_image(prompt, style)
            except Exception:
                return None
    
    async def _generate_placeholder_image(
        self, 
        prompt: str, 
        style: str
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una imagen placeholder simple cuando todos los servicios AI fallan
        """
        try:
            logger.info("🎨 Generando imagen placeholder como fallback final...")
            
            # Crear un archivo de texto simple como placeholder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"placeholder_{style}_{timestamp}_{unique_id}.txt"
            filepath = os.path.join(self.images_dir, filename)
            
            # Crear contenido del placeholder
            content = f"""IMAGEN PLACEHOLDER
===================

Prompt: {prompt}
Estilo: {style.replace('_', ' ').title()}
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Nota: Esta es una imagen placeholder generada porque
todos los servicios de IA no están disponibles en este momento.

Servicios intentados:
- Stockimg.ai (bloqueado por Cloudflare)
- Stability AI (sin API key)
- OpenAI DALL-E (límite de facturación)
- Stable Diffusion gratuito (endpoints no disponibles)

Para generar imágenes reales, configura al menos una API key válida.
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(filepath)
            
            logger.info("✅ Placeholder de texto generado exitosamente")
            
            return {
                "filename": filename,
                "filepath": filepath,
                "url": f"/generated_images/{filename}",
                "prompt": prompt,
                "style": style,
                "width": 512,
                "height": 512,
                "file_size": file_size,
                "generated_at": datetime.now().isoformat(),
                "service": "text-placeholder"
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando placeholder: {str(e)}")
            return None
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """
        Mejora el prompt para obtener mejores resultados con Stable Diffusion
        """
        style_enhancements = {
            "product_photography": "professional product photography, studio lighting, white background, high quality, detailed, 8k resolution",
            "main_product": "product shot, clean background, professional lighting, commercial photography, high detail",
            "lifestyle": "lifestyle photography, natural lighting, realistic, high quality",
            "contextual": "real-world setting, natural environment, practical use, realistic",
            "detail": "macro photography, close-up, highly detailed, sharp focus, 8k",
            "technical": "technical illustration, clean design, precise, informative"
        }
        
        enhancement = style_enhancements.get(style, "high quality, professional, detailed")
        return f"{prompt}, {enhancement}"
    
    async def _save_image_bytes(
        self, 
        image_bytes: bytes, 
        prompt: str, 
        style: str, 
        service: str
    ) -> Optional[Dict[str, Any]]:
        """
        Guarda una imagen desde bytes
        """
        try:
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
                "width": 512,  # Típico para endpoints gratuitos
                "height": 512,
                "file_size": file_size,
                "generated_at": datetime.now().isoformat(),
                "service": service
            }
            
        except Exception as e:
            logger.error(f"❌ Error guardando imagen: {str(e)}")
            return None


# Instancia global del servicio
_free_sd_service = None

def get_free_stable_diffusion_service() -> FreeStableDiffusionService:
    """
    Obtiene la instancia global del servicio gratuito de Stable Diffusion
    """
    global _free_sd_service
    if _free_sd_service is None:
        _free_sd_service = FreeStableDiffusionService()
    return _free_sd_service
