from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..services.ollama_service import get_ollama_service
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Clase base para todos los agentes de IA especializados
    """
    
    def __init__(self, agent_name: str, temperature: float = 0.7):
        self.agent_name = agent_name
        self.temperature = temperature
        self.ollama_service = get_ollama_service()
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Retorna el prompt del sistema específico para este agente
        """
        pass
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa los datos de entrada y retorna una respuesta estructurada
        """
        pass
    
    async def _generate_response(
        self, 
        prompt: str, 
        structured: bool = True,
        expected_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Método helper para generar respuestas usando Ollama
        """
        start_time = datetime.now()
        
        try:
            if structured:
                response = await self.ollama_service.generate_structured_response(
                    prompt=prompt,
                    system_prompt=self.get_system_prompt(),
                    expected_format=expected_format,
                    temperature=self.temperature
                )
            else:
                response = await self.ollama_service.generate_response(
                    prompt=prompt,
                    system_prompt=self.get_system_prompt(),
                    temperature=self.temperature
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            response["processing_time"] = processing_time
            
            return response
            
        except Exception as e:
            logger.error(f"Error en agente {self.agent_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def _create_agent_response(
        self, 
        data: Dict[str, Any], 
        confidence: float,
        status: str = "success",
        processing_time: float = 0.0,
        notes: Optional[list] = None,
        recommendations: Optional[list] = None
    ) -> AgentResponse:
        """
        Crea una respuesta estándar del agente
        """
        return AgentResponse(
            agent_name=self.agent_name,
            status=status,
            data=data,
            confidence=confidence,
            processing_time=processing_time,
            notes=notes or [],
            recommendations=recommendations or []
        )
