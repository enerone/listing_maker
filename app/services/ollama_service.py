import ollama
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, model_name: str = "qwen2.5:latest", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        try:
            self.client = ollama.Client(host=host)
            logger.info(f"Cliente Ollama inicializado - Modelo: {model_name}, Host: {host}")
        except Exception as e:
            logger.error(f"Error inicializando cliente Ollama: {str(e)}")
            self.client = None
        
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera una respuesta usando Ollama
        """
        try:
            if not self.client:
                raise Exception("Cliente Ollama no inicializado correctamente")
                
            start_time = datetime.now()
            
            # Preparar mensajes
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            logger.debug(f"Enviando prompt a Ollama: {prompt[:100]}...")
            
            # Llamar a Ollama de forma más simple
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat,
                    model=self.model_name,
                    messages=messages,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens or 1000
                    }
                ),
                timeout=120.0  # Aumentar timeout a 2 minutos para CPU
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Extraer contenido de la respuesta de forma más robusta
            content = ""
            
            try:
                # Intentar diferentes formas de extraer el contenido
                if hasattr(response, 'message'):
                    message = getattr(response, 'message')
                    if hasattr(message, 'content'):
                        content = getattr(message, 'content')
                    else:
                        content = str(message)
                elif isinstance(response, dict):
                    if 'message' in response and isinstance(response['message'], dict):
                        content = response['message'].get('content', '')
                    elif 'response' in response:
                        content = response['response']
                    else:
                        content = str(response)
                else:
                    content = str(response)
                    
            except Exception as e:
                logger.warning(f"Error extrayendo contenido: {e}")
                content = str(response)
            
            logger.debug(f"Respuesta de Ollama: {content[:200]}...")
            
            return {
                "success": True,
                "content": content,
                "processing_time": processing_time,
                "model": self.model_name,
                "tokens_used": 0
            }
            
        except asyncio.TimeoutError:
            logger.error("Timeout al esperar respuesta de Ollama")
            return {
                "success": False,
                "error": "Timeout al esperar respuesta de Ollama",
                "processing_time": 0,
                "content": None
            }
        except Exception as e:
            logger.error(f"Error en generación Ollama: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0,
                "content": None
            }
    
    async def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        expected_format: str = "json",
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Genera una respuesta estructurada (JSON) usando Ollama
        """
        structured_system = f"""
        {system_prompt or ''}
        
        IMPORTANTE: Tu respuesta debe ser únicamente un objeto JSON válido en formato {expected_format}.
        No incluyas explicaciones adicionales, comentarios o texto antes o después del JSON.
        Asegúrate de que el JSON sea válido y parseable.
        """
        
        response = await self.generate_response(
            prompt=prompt,
            system_prompt=structured_system,
            temperature=temperature
        )
        
        if response["success"]:
            try:
                # Intentar parsear el JSON
                content = response["content"].strip()
                # Limpiar posibles marcadores de código
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                parsed_data = json.loads(content)
                response["parsed_data"] = parsed_data
                response["is_structured"] = True
                
            except json.JSONDecodeError as e:
                logger.warning(f"Error parseando JSON: {str(e)}")
                response["is_structured"] = False
                response["parse_error"] = str(e)
        
        return response
    
    async def check_model_availability(self) -> bool:
        """
        Verifica si el modelo está disponible
        """
        try:
            if not self.client:
                logger.error("Cliente Ollama no inicializado")
                return False
                
            models = await asyncio.to_thread(self.client.list)
            available_models = [model['name'] for model in models.get('models', [])]
            return self.model_name in available_models
        except Exception as e:
            logger.error(f"Error verificando modelo: {str(e)}")
            return False
    
    async def pull_model_if_needed(self) -> bool:
        """
        Descarga el modelo si no está disponible
        """
        try:
            if not self.client:
                logger.error("Cliente Ollama no inicializado")
                return False
                
            if not await self.check_model_availability():
                logger.info(f"Descargando modelo {self.model_name}...")
                await asyncio.to_thread(self.client.pull, self.model_name)
                return True
            return True
        except Exception as e:
            logger.error(f"Error descargando modelo: {str(e)}")
            return False

# Singleton para reutilizar la conexión
_ollama_service = None

def get_ollama_service() -> OllamaService:
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service
