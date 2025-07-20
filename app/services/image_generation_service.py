"""
Servicio de generación de imágenes usando Stable Diffusion
"""
import os
import logging
import torch
from typing import List, Optional, Dict, Any, Union
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import uuid

try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """
    Servicio para generar imágenes usando Stable Diffusion
    """
    
    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "runwayml/stable-diffusion-v1-5"  # Modelo base
        self.images_dir = "generated_images"
        self.executor = ThreadPoolExecutor(max_workers=1)  # Una sola GPU/CPU
        
        # Crear directorio de imágenes si no existe
        os.makedirs(self.images_dir, exist_ok=True)
        
        logger.info(f"🎨 ImageGenerationService inicializado - Device: {self.device}")
    
    async def initialize_pipeline(self) -> bool:
        """
        Inicializa el pipeline de Stable Diffusion
        """
        if not DIFFUSERS_AVAILABLE:
            logger.error("❌ Librerías de diffusers no disponibles")
            return False
        
        if self.pipeline is not None:
            return True
        
        try:
            logger.info("🚀 Cargando modelo Stable Diffusion...")
            
            # Ejecutar en thread separado para no bloquear
            loop = asyncio.get_event_loop()
            self.pipeline = await loop.run_in_executor(
                self.executor, 
                self._load_pipeline
            )
            
            logger.info(f"✅ Pipeline cargado exitosamente en {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando pipeline: {str(e)}")
            return False
    
    def _load_pipeline(self):
        """
        Carga el pipeline en el thread executor
        """
        try:
            pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,  # Desactivar para mayor velocidad
                requires_safety_checker=False
            )
            
            # Optimizar scheduler para mejor calidad/velocidad
            pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                pipeline.scheduler.config
            )
            
            pipeline = pipeline.to(self.device)
            
            # Optimizaciones para GPU (solo las que existen)
            if self.device == "cuda":
                pipeline.enable_attention_slicing()
                # Intentar optimizaciones adicionales si están disponibles
                try:
                    pipeline.enable_memory_efficient_attention()
                except AttributeError:
                    logger.info("enable_memory_efficient_attention no disponible en esta versión")
                
                try:
                    pipeline.enable_xformers_memory_efficient_attention()
                except (AttributeError, ImportError):
                    logger.info("xformers no disponible, usando optimizaciones estándar")
            
            return pipeline
            
        except Exception as e:
            logger.error(f"Error cargando pipeline: {str(e)}")
            raise e
    
    async def generate_product_images(
        self, 
        product_name: str, 
        description: str, 
        num_images: int = 3,
        style: str = "product_photography"
    ) -> List[Dict[str, Any]]:
        """
        Genera imágenes para un producto basado en su descripción
        
        Args:
            product_name: Nombre del producto
            description: Descripción del producto
            num_images: Número de imágenes a generar
            style: Estilo de imagen ('product_photography', 'lifestyle', 'technical', 'infographic')
            
        Returns:
            Lista de diccionarios con información de las imágenes generadas
        """
        if not await self.initialize_pipeline():
            return []
        
        try:
            logger.info(f"🎨 Generando {num_images} imágenes para: {product_name}")
            
            # Crear prompts optimizados
            prompts = self._create_prompts(product_name, description, style, num_images)
            
            # Generar imágenes
            generated_images = []
            for i, prompt in enumerate(prompts):
                try:
                    image_info = await self._generate_single_image(
                        prompt, 
                        f"{product_name}_{style}_{i+1}"
                    )
                    if image_info:
                        generated_images.append(image_info)
                        
                except Exception as e:
                    logger.error(f"❌ Error generando imagen {i+1}: {str(e)}")
                    continue
            
            logger.info(f"✅ Generadas {len(generated_images)} imágenes exitosamente")
            return generated_images
            
        except Exception as e:
            logger.error(f"❌ Error en generación de imágenes: {str(e)}")
            return []
    
    def _create_prompts(
        self, 
        product_name: str, 
        description: str, 
        style: str, 
        num_images: int
    ) -> List[str]:
        """
        Crea prompts optimizados para diferentes estilos de imagen
        """
        base_product = f"{product_name}, {description}"
        
        style_templates = {
            "product_photography": [
                f"professional product photography of {base_product}, white background, studio lighting, high resolution, commercial photography, clean aesthetic",
                f"clean product shot of {base_product}, minimal background, soft shadows, professional lighting, e-commerce style",
                f"detailed product image of {base_product}, white backdrop, commercial photography, sharp focus, high quality"
            ],
            "lifestyle": [
                f"lifestyle photography showing {base_product} in use, natural setting, person using product, realistic scenario",
                f"{base_product} in everyday environment, natural lighting, lifestyle context, authentic usage",
                f"real-world application of {base_product}, lifestyle setting, natural photography, user interaction"
            ],
            "technical": [
                f"technical diagram of {base_product}, cutaway view, detailed components, engineering drawing style",
                f"exploded view of {base_product}, technical illustration, detailed parts, clean technical drawing",
                f"technical specification illustration of {base_product}, blueprint style, detailed measurements"
            ],
            "infographic": [
                f"infographic showing {base_product} features, clean design, modern layout, feature highlights",
                f"product benefits infographic for {base_product}, visual comparison, feature breakdown",
                f"comparison chart featuring {base_product}, clean infographic design, benefit visualization"
            ]
        }
        
        templates = style_templates.get(style, style_templates["product_photography"])
        
        # Repetir templates si necesitamos más imágenes
        prompts = []
        for i in range(num_images):
            template_index = i % len(templates)
            prompts.append(templates[template_index])
        
        return prompts
    
    async def _generate_single_image(
        self, 
        prompt: str, 
        filename_base: str
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una sola imagen usando el prompt
        """
        try:
            # Ejecutar generación en thread separado
            loop = asyncio.get_event_loop()
            image = await loop.run_in_executor(
                self.executor,
                self._run_pipeline,
                prompt
            )
            
            # Guardar imagen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{filename_base}_{timestamp}_{unique_id}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            image.save(filepath, "JPEG", quality=85, optimize=True)
            
            # Obtener información de la imagen
            width, height = image.size
            file_size = os.path.getsize(filepath)
            
            return {
                "filename": filename,
                "filepath": filepath,
                "url": f"/generated_images/{filename}",
                "prompt": prompt,
                "width": width,
                "height": height,
                "file_size": file_size,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando imagen: {str(e)}")
            return None
    
    def _run_pipeline(self, prompt: str):
        """
        Ejecuta el pipeline de generación
        """
        if self.pipeline is None:
            raise ValueError("Pipeline no inicializado correctamente")
        
        # Prompt negativo para mejorar calidad
        negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, extra limbs, poorly drawn, deformed"
        
        # Generar imagen
        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=20,  # Balance entre calidad y velocidad
            guidance_scale=7.5,      # Control de adherencia al prompt
            width=512,               # Resolución estándar
            height=512,
            num_images_per_prompt=1
        )
        
        # Extraer la imagen del resultado
        # El pipeline devuelve StableDiffusionPipelineOutput con .images
        return result.images[0]
    
    async def generate_variation(
        self, 
        original_prompt: str, 
        variation_type: str = "style"
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una variación de una imagen existente
        
        Args:
            original_prompt: Prompt original
            variation_type: Tipo de variación ('style', 'angle', 'lighting', 'background')
        """
        if not await self.initialize_pipeline():
            return None
        
        # Modificar prompt según tipo de variación
        modified_prompt = self._modify_prompt_for_variation(original_prompt, variation_type)
        
        return await self._generate_single_image(
            modified_prompt, 
            f"variation_{variation_type}"
        )
    
    def _modify_prompt_for_variation(self, prompt: str, variation_type: str) -> str:
        """
        Modifica el prompt para crear variaciones
        """
        variations = {
            "style": f"{prompt}, different artistic style, alternative composition",
            "angle": f"{prompt}, different camera angle, alternative perspective",
            "lighting": f"{prompt}, different lighting setup, alternative mood",
            "background": f"{prompt}, different background, alternative setting"
        }
        
        return variations.get(variation_type, prompt)
    
    def get_generated_images_info(self) -> List[Dict[str, Any]]:
        """
        Obtiene información de todas las imágenes generadas
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
                        "url": f"/generated_images/{filename}",
                        "file_size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error obteniendo info de {filename}: {str(e)}")
                    continue
        
        # Ordenar por fecha de creación (más recientes primero)
        images_info.sort(key=lambda x: x["created_at"], reverse=True)
        return images_info
    
    def cleanup_old_images(self, max_images: int = 100):
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
                        logger.info(f"🗑️ Imagen antigua eliminada: {image_info['filename']}")
                    except Exception as e:
                        logger.error(f"Error eliminando {image_info['filename']}: {str(e)}")
                
                logger.info(f"🧹 Limpieza completada: {len(to_delete)} imágenes eliminadas")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de imágenes: {str(e)}")
    
    async def generate_images_from_ai_prompts(
        self,
        product_name: str,
        ai_prompts: Dict[str, str],
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Genera imágenes usando los prompts específicos creados por el agente copywriter
        
        Args:
            product_name: Nombre del producto
            ai_prompts: Diccionario con prompts IA del agente copywriter
            session_id: ID de sesión para tracking
            
        Returns:
            Lista de diccionarios con información de las imágenes generadas
        """
        if not await self.initialize_pipeline():
            return []
        
        try:
            logger.info(f"🎨 Generando imágenes con prompts IA para: {product_name}")
            
            # Validar que tenemos prompts válidos
            valid_prompts = {k: v for k, v in ai_prompts.items() if v and v.strip()}
            if not valid_prompts:
                logger.warning("⚠️ No hay prompts IA válidos, usando generación estándar")
                return await self.generate_product_images(product_name, "", 3)
            
            # Generar imágenes para cada prompt
            generated_images = []
            for prompt_type, prompt_text in valid_prompts.items():
                try:
                    # Mejorar el prompt con términos técnicos de calidad
                    enhanced_prompt = self._enhance_ai_prompt(prompt_text, prompt_type)
                    
                    image_info = await self._generate_single_image(
                        enhanced_prompt,
                        f"{product_name}_{prompt_type}"
                    )
                    
                    if image_info:
                        image_info['prompt_type'] = prompt_type
                        image_info['original_prompt'] = prompt_text
                        generated_images.append(image_info)
                        
                except Exception as e:
                    logger.error(f"❌ Error generando imagen {prompt_type}: {str(e)}")
                    continue
            
            logger.info(f"✅ Generadas {len(generated_images)} imágenes con prompts IA")
            return generated_images
            
        except Exception as e:
            logger.error(f"❌ Error en generación con prompts IA: {str(e)}")
            return []
    
    def _enhance_ai_prompt(self, base_prompt: str, prompt_type: str) -> str:
        """
        Mejora un prompt IA básico con términos técnicos y de calidad
        """
        # Términos de calidad general
        quality_terms = "high quality, professional, detailed, 8k resolution, studio lighting"
        
        # Términos específicos por tipo de imagen
        type_enhancements = {
            "main_product": "product photography, clean background, professional lighting, commercial quality",
            "contextual": "realistic environment, natural lighting, lifestyle photography, authentic setting", 
            "lifestyle": "lifestyle photography, aspirational, professional models, high-end atmosphere",
            "detail": "macro photography, texture detail, material showcase, close-up, premium quality",
            "comparative": "comparison shot, side by side, clear demonstration, infographic style, educational"
        }
        
        specific_terms = type_enhancements.get(prompt_type, "professional photography")
        
        # Combinar el prompt base con mejoras
        enhanced = f"{base_prompt}, {specific_terms}, {quality_terms}"
        
        return enhanced

# Instancia global del servicio
_image_service = None

def get_image_generation_service() -> ImageGenerationService:
    """
    Obtiene la instancia global del servicio de generación de imágenes
    """
    global _image_service
    if _image_service is None:
        _image_service = ImageGenerationService()
    return _image_service
