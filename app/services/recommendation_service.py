"""
Servicio para aplicar recomendaciones a listings
"""
import logging
import json
from typing import Dict, Any, Optional
from ..models.database_models import Listing
from ..services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class RecommendationService:
    """Servicio para aplicar recomendaciones inteligentes a listings"""
    
    def __init__(self):
        self.ollama_service = OllamaService()
    
    async def apply_recommendation_with_llm(
        self,
        listing: Listing, 
        agent_name: str, 
        recommendation_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        Aplica recomendaciones usando LLM para interpretar y generar cambios inteligentes
        """
        try:
            current_context = self._build_listing_context(listing)
            prompt = self._build_recommendation_prompt(agent_name, recommendation_text, current_context)
            
            # Obtener respuesta del LLM
            ollama_response = await self.ollama_service.generate_response(prompt)
            response_content = ollama_response.get("content", "")
            
            if not response_content:
                logger.warning("LLM no generó respuesta para aplicar recomendación")
                return None
                
            return self._parse_llm_response(response_content)
            
        except Exception as e:
            logger.error(f"Error aplicando recomendación con LLM: {str(e)}")
            return self._apply_fallback_logic(listing, recommendation_text)
    
    def _build_listing_context(self, listing: Listing) -> Dict[str, Any]:
        """Construir contexto del listing actual"""
        return {
            "title": str(listing.title or ""),
            "description": str(listing.description or ""),
            "price": float(getattr(listing, 'target_price', None) or 0),
            "bullet_points": listing.bullet_points or [],
            "keywords": listing.backend_keywords or [],
            "product_name": str(listing.product_name or ""),
            "category": str(listing.category or "")
        }
    
    def _build_recommendation_prompt(
        self, 
        agent_name: str, 
        recommendation_text: str, 
        context: Dict[str, Any]
    ) -> str:
        """Construir prompt para el LLM"""
        return f"""
Eres un experto en optimización de listings de Amazon. Analiza la recomendación y sugiere cambios específicos.

RECOMENDACIÓN A APLICAR:
Agente: {agent_name}
Recomendación: {recommendation_text}

ESTADO ACTUAL DEL LISTING:
Título: {context['title']}
Descripción: {context['description'][:500]}...
Precio: ${context['price']}
Bullet Points: {context['bullet_points']}
Keywords: {context['keywords']}
Producto: {context['product_name']}
Categoría: {context['category']}

FORMATO DE RESPUESTA (JSON válido):
{{
    "changes_needed": true/false,
    "updated_fields": {{
        "title": "Nuevo título si aplica cambio, null si no",
        "description": "Nueva descripción si aplica cambio, null si no", 
        "target_price": número_si_aplica_cambio_o_null,
        "bullet_points": ["Lista de nuevos bullet points si aplica"] o null,
        "backend_keywords": ["Lista de nuevas keywords si aplica"] o null
    }},
    "explanation": "Explicación de cambios",
    "applied_recommendation": "Resumen de aplicación"
}}

INSTRUCCIONES:
- Solo modifica campos relacionados con la recomendación
- Si no se puede aplicar automáticamente, marca changes_needed como false
- Mantén coherencia con el estilo existente
- Para precios, solo sugiere cambios si la recomendación es específicamente sobre pricing
"""
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parsear respuesta JSON del LLM"""
        try:
            llm_result = json.loads(response)
            
            if not llm_result.get("changes_needed", False):
                logger.info("LLM determinó que no se necesitan cambios automáticos")
                return None
                
            # Extraer campos actualizados
            updated_fields = {}
            llm_fields = llm_result.get("updated_fields", {})
            
            for field, value in llm_fields.items():
                if value is not None and value != "":
                    if field == "target_price" and isinstance(value, (int, float)):
                        updated_fields[field] = value
                    elif field in ["title", "description", "bullet_points", "backend_keywords"]:
                        updated_fields[field] = value
            
            logger.info(f"LLM sugirió cambios: {list(updated_fields.keys())}")
            logger.info(f"Explicación LLM: {llm_result.get('explanation', 'N/A')}")
            
            return updated_fields if updated_fields else None
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM JSON response: {e}")
            logger.debug(f"LLM Raw response: {response[:500]}...")
            return None
    
    def _apply_fallback_logic(self, listing: Listing, recommendation_text: str) -> Optional[Dict[str, Any]]:
        """Lógica de fallback simplificada"""
        updated_fields = {}
        recommendation_lower = recommendation_text.lower()
        
        try:
            # Recomendación de título con marca
            if "brand name" in recommendation_lower or "discoverability" in recommendation_lower:
                current_title = str(listing.title or listing.product_name or "")
                if "TechPro" not in current_title and current_title:
                    updated_fields["title"] = f"TechPro {current_title}"
            
            # Recomendación de precio
            elif "price" in recommendation_lower and ("adjust" in recommendation_lower or "competitive" in recommendation_lower):
                current_price = getattr(listing, 'target_price', None)
                if current_price and current_price > 0:
                    updated_fields["target_price"] = round(float(current_price) * 1.05, 2)
            
            # Recomendación de keywords
            elif "keyword" in recommendation_lower or "seo" in recommendation_lower:
                current_keywords = getattr(listing, 'backend_keywords', None) or []
                if isinstance(current_keywords, str):
                    current_keywords = [kw.strip() for kw in current_keywords.split(',') if kw.strip()]
                elif not isinstance(current_keywords, list):
                    current_keywords = []
                
                new_keywords = current_keywords.copy() if current_keywords else []
                suggested = ["premium", "quality"]
                
                for kw in suggested:
                    if kw not in new_keywords:
                        new_keywords.append(kw)
                
                if new_keywords != current_keywords:
                    updated_fields["backend_keywords"] = new_keywords
            
            return updated_fields if updated_fields else None
            
        except Exception as e:
            logger.error(f"Error en fallback: {str(e)}")
            return None
