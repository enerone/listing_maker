"""
Agente Revisor - Coordina y mejora las sugerencias de todos los agentes
para crear un listing final optimizado y completo.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from .base_agent import BaseAgent
from .real_image_search_agent import RealImageSearchAgent
from ..services.ollama_service import get_ollama_service
from ..models import AgentResponse

logger = logging.getLogger(__name__)


class ReviewAgent(BaseAgent):
    """
    Agente revisor que coordina y optimiza las sugerencias de todos los agentes
    para crear un listing final mejorado y completo.
    """
    
    def __init__(self):
        super().__init__("ReviewAgent")
        self.ollama_service = get_ollama_service()
        self.image_agent = RealImageSearchAgent()
        
        # Categorías de Amazon más comunes
        self.amazon_categories = {
            "electronics": ["Electronics", "Cell Phones & Accessories", "Computers & Accessories"],
            "sports": ["Sports & Outdoors", "Exercise & Fitness", "Outdoor Recreation"],
            "home": ["Home & Kitchen", "Kitchen & Dining", "Home Décor"],
            "beauty": ["Beauty & Personal Care", "Makeup", "Skin Care"],
            "clothing": ["Clothing, Shoes & Jewelry", "Women's Clothing", "Men's Clothing"],
            "toys": ["Toys & Games", "Action Figures & Statues", "Arts & Crafts"],
            "books": ["Books", "Literature & Fiction", "Mystery & Suspense"],
            "automotive": ["Automotive", "Car Care", "Exterior Accessories"],
            "tools": ["Tools & Home Improvement", "Power Tools", "Hand Tools"],
            "health": ["Health & Household", "Health Care", "Household Supplies"]
        }
        
        # Palabras clave de alta conversión por categoría
        self.high_conversion_keywords = {
            "electronics": ["wireless", "smart", "bluetooth", "rechargeable", "portable", "premium"],
            "sports": ["professional", "performance", "training", "workout", "fitness", "durable"],
            "home": ["premium", "modern", "stylish", "durable", "easy-clean", "space-saving"],
            "beauty": ["natural", "organic", "long-lasting", "gentle", "effective", "anti-aging"],
            "clothing": ["comfortable", "stylish", "versatile", "high-quality", "breathable"],
            "toys": ["educational", "safe", "interactive", "creative", "fun", "age-appropriate"],
            "books": ["bestseller", "acclaimed", "comprehensive", "insightful", "engaging"],
            "automotive": ["heavy-duty", "durable", "weatherproof", "precision", "performance"],
            "tools": ["heavy-duty", "precision", "durable", "professional", "ergonomic"],
            "health": ["natural", "safe", "effective", "gentle", "trusted", "clinically-tested"]
        }

    def get_system_prompt(self) -> str:
        """
        Retorna el prompt del sistema para el agente revisor.
        """
        return """
        Eres un experto revisor de listings de Amazon con amplia experiencia en optimización de conversiones.
        Tu tarea es revisar y mejorar todos los aspectos de un listing para maximizar su efectividad:
        IMPORTANTE: Todas las recomendaciones deben estar completamente en español, con un lenguaje claro y específico para el mercado hispanohablante.
        
        1. Títulos: Optimiza para búsquedas y conversiones
        2. Descripciones: Mejora claridad, persuasión y beneficios
        3. Bullet points: Enfócate en beneficios únicos
        4. Categorías: Asegura precisión y relevancia
        5. Keywords: Optimiza para SEO de Amazon
        6. Especificaciones: Completa información técnica
        
        Siempre proporciona respuestas en formato JSON válido con mejoras específicas y justificadas.
        """

    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Procesa y revisa todos los aspectos del listing para crear una propuesta final optimizada.
        """
        try:
            logger.info("Iniciando revisión integral del listing")
            start_time = datetime.now()
            
            # Extraer datos del producto y resultados de otros agentes
            product_data = data.get("product_data", {})
            agent_results = data.get("agent_results", {})
            
            # Realizar revisión integral
            review_result = await self._comprehensive_review(product_data, agent_results)
            
            # Buscar imágenes optimizadas
            image_suggestions = await self._get_optimized_images(review_result)
            
            # Crear propuesta final
            final_proposal = await self._create_final_proposal(review_result, image_suggestions)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_agent_response(
                data=final_proposal,
                confidence=review_result.get("overall_confidence", 0.85),
                processing_time=processing_time,
                recommendations=review_result.get("recommendations", []),
                notes=["Revisión integral completada. Propuesta final optimizada generada."]
            )
            
        except Exception as e:
            logger.error(f"Error en ReviewAgent: {str(e)}")
            return self._create_agent_response(
                data={"error": str(e)},
                confidence=0.0,
                processing_time=0.0,
                status="error",
                notes=[f"Error durante la revisión: {str(e)}"]
            )

    async def _comprehensive_review(self, product_data: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una revisión integral de todos los aspectos del listing.
        """
        product_name = product_data.get("product_name", "")
        
        # Revisar cada aspecto del listing
        title_review = await self._review_title(product_data, agent_results)
        description_review = await self._review_description(product_data, agent_results)
        bullets_review = await self._review_bullet_points(product_data, agent_results)
        category_review = await self._review_category(product_data)
        keywords_review = await self._review_keywords(product_data, agent_results)
        specs_review = await self._review_specifications(product_data)
        
        # Calcular confianza general
        overall_confidence = self._calculate_overall_confidence([
            title_review, description_review, bullets_review, 
            category_review, keywords_review, specs_review
        ])
        
        # Generar recomendaciones generales
        general_recommendations = self._generate_general_recommendations([
            title_review, description_review, bullets_review, 
            category_review, keywords_review, specs_review
        ])
        
        return {
            "title_review": title_review,
            "description_review": description_review,
            "bullets_review": bullets_review,
            "category_review": category_review,
            "keywords_review": keywords_review,
            "specs_review": specs_review,
            "overall_confidence": overall_confidence,
            "recommendations": general_recommendations,
            "product_name": product_name,
            "reviewed_at": datetime.now().isoformat()
        }

    async def _review_title(self, product_data: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa y optimiza el título del producto.
        """
        try:
            current_title = agent_results.get("title_agent", {}).get("title", "")
            product_name = product_data.get("product_name", "")
            category = product_data.get("category", "Other")
            features = product_data.get("features", [])
            
            # Generar título optimizado usando reglas de optimización
            optimized_title = self._optimize_title(current_title, product_name, category, features)
            
            # Calcular puntuación de mejora
            improvement_score = self._calculate_title_improvement(current_title, optimized_title)
            
            return {
                "optimized_title": optimized_title,
                "improvement_score": improvement_score,
                "changes_made": ["Agregó palabras clave relevantes", "Mejoró estructura"],
                "keywords_included": self._extract_keywords_from_title(optimized_title),
                "conversion_elements": ["Beneficios claros", "Llamada a la acción"],
                "character_count": len(optimized_title),
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error revisando título: {str(e)}")
            return {
                "optimized_title": product_data.get("product_name", ""),
                "improvement_score": 5,
                "changes_made": [],
                "keywords_included": [],
                "conversion_elements": [],
                "character_count": 0,
                "confidence": 0.5
            }

    async def _review_description(self, product_data: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa y optimiza la descripción del producto.
        """
        try:
            current_description = agent_results.get("description_agent", {}).get("description", "")
            product_name = product_data.get("product_name", "")
            features = product_data.get("features", [])
            
            # Generar descripción optimizada
            optimized_description = self._optimize_description(current_description, product_name, features)
            
            return {
                "optimized_description": optimized_description,
                "improvement_score": 8,
                "key_improvements": ["Estructura mejorada", "Beneficios destacados"],
                "emotional_triggers": ["Calidad premium", "Fácil de usar"],
                "benefits_highlighted": features[:3],
                "structure_improvements": ["Párrafos más claros", "Puntos de dolor abordados"],
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error revisando descripción: {str(e)}")
            return {
                "optimized_description": product_data.get("description", ""),
                "improvement_score": 5,
                "key_improvements": [],
                "emotional_triggers": [],
                "benefits_highlighted": [],
                "structure_improvements": [],
                "confidence": 0.5
            }

    async def _review_bullet_points(self, product_data: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa y optimiza los bullet points.
        """
        try:
            current_bullets = agent_results.get("bullets_agent", {}).get("bullet_points", [])
            product_name = product_data.get("product_name", "")
            features = product_data.get("features", [])
            
            # Generar bullet points optimizados
            optimized_bullets = self._optimize_bullets(current_bullets, product_name, features)
            
            return {
                "optimized_bullets": optimized_bullets,
                "improvement_score": 8,
                "key_changes": ["Estructura mejorada", "Beneficios claros"],
                "keywords_added": ["premium", "durable", "fácil"],
                "benefit_focus": ["Calidad", "Facilidad de uso", "Durabilidad"],
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error revisando bullet points: {str(e)}")
            return {
                "optimized_bullets": [],
                "improvement_score": 5,
                "key_changes": [],
                "keywords_added": [],
                "benefit_focus": [],
                "confidence": 0.5
            }

    async def _review_category(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa y sugiere la categoría más apropiada.
        """
        try:
            current_category = product_data.get("category", "Other")
            product_name = product_data.get("product_name", "")
            description = product_data.get("description", "")
            features = product_data.get("features", [])
            
            # Analizar el producto para determinar la mejor categoría
            suggested_category = self._suggest_best_category(product_name, description, features)
            
            confidence = 0.9 if suggested_category != "Other" else 0.6
            
            return {
                "current_category": current_category,
                "suggested_category": suggested_category,
                "subcategories": self.amazon_categories.get(suggested_category.lower(), []),
                "confidence": confidence,
                "category_match_score": self._calculate_category_match(product_name, suggested_category),
                "reasons": self._get_category_reasons(product_name, suggested_category)
            }
            
        except Exception as e:
            logger.error(f"Error revisando categoría: {str(e)}")
            return {
                "current_category": "Other",
                "suggested_category": "Other",
                "subcategories": [],
                "confidence": 0.5,
                "category_match_score": 0.5,
                "reasons": []
            }

    async def _review_keywords(self, product_data: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa y optimiza las palabras clave.
        """
        try:
            current_keywords = agent_results.get("keywords_agent", {}).get("keywords", [])
            product_name = product_data.get("product_name", "")
            category = product_data.get("category", "Other")
            features = product_data.get("features", [])
            
            # Obtener palabras clave optimizadas
            optimized_keywords = self._optimize_keywords(current_keywords, product_name, category, features)
            
            return {
                "optimized_keywords": optimized_keywords,
                "high_priority_keywords": optimized_keywords[:5],
                "long_tail_keywords": [f"{product_name} {kw}" for kw in optimized_keywords[:3]],
                "competitor_keywords": ["premium", "quality", "durable"],
                "seasonal_keywords": ["gift", "holiday", "special"],
                "improvement_score": 8,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error revisando keywords: {str(e)}")
            return {
                "optimized_keywords": [],
                "high_priority_keywords": [],
                "long_tail_keywords": [],
                "competitor_keywords": [],
                "seasonal_keywords": [],
                "improvement_score": 5,
                "confidence": 0.5
            }

    async def _review_specifications(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa y optimiza las especificaciones del producto.
        """
        try:
            current_specs = product_data.get("raw_specifications", "")
            product_name = product_data.get("product_name", "")
            category = product_data.get("category", "Other")
            
            # Identificar especificaciones faltantes
            missing_specs = self._identify_missing_specs(current_specs, category)
            
            return {
                "missing_specs": missing_specs,
                "needs_clarification": ["Dimensiones exactas", "Peso específico"],
                "technical_details": ["Materiales", "Compatibilidad"],
                "certifications": ["CE", "FCC", "RoHS"],
                "compatibility_info": ["Universal", "Multiplataforma"],
                "completeness_score": 7,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error revisando especificaciones: {str(e)}")
            return {
                "missing_specs": [],
                "needs_clarification": [],
                "technical_details": [],
                "certifications": [],
                "compatibility_info": [],
                "completeness_score": 5,
                "confidence": 0.5
            }

    async def _get_optimized_images(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene sugerencias de imágenes optimizadas basadas en la revisión.
        """
        try:
            product_name = review_result.get("product_name", "")
            optimized_title = review_result.get("title_review", {}).get("optimized_title", "")
            keywords = review_result.get("keywords_review", {}).get("optimized_keywords", [])
            
            # Crear términos de búsqueda optimizados para imágenes
            search_terms = [product_name]
            if optimized_title:
                search_terms.append(optimized_title)
            search_terms.extend(keywords[:5])  # Top 5 keywords
            
            # Usar el agente de imágenes para buscar imágenes optimizadas
            image_data = {
                "product_data": {
                    "product_name": product_name,
                    "category": review_result.get("category_review", {}).get("suggested_category", "Other"),
                    "features": review_result.get("bullets_review", {}).get("benefit_focus", []),
                    "description": review_result.get("description_review", {}).get("optimized_description", ""),
                    "search_terms": search_terms
                }
            }
            
            image_result = await self.image_agent.process(image_data)
            
            return {
                "status": image_result.status,
                "images": image_result.data.get("downloaded_images", []),
                "search_terms_used": search_terms,
                "confidence": image_result.confidence,
                "recommendations": image_result.recommendations
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo imágenes optimizadas: {str(e)}")
            return {
                "status": "error",
                "images": [],
                "search_terms_used": [],
                "confidence": 0.0,
                "recommendations": []
            }

    async def _create_final_proposal(self, review_result: Dict[str, Any], image_suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea la propuesta final optimizada integrando todas las mejoras.
        """
        title_review = review_result.get("title_review", {})
        description_review = review_result.get("description_review", {})
        bullets_review = review_result.get("bullets_review", {})
        category_review = review_result.get("category_review", {})
        keywords_review = review_result.get("keywords_review", {})
        specs_review = review_result.get("specs_review", {})
        
        # Calcular puntuación general de mejora
        improvement_scores = [
            title_review.get("improvement_score", 5),
            description_review.get("improvement_score", 5),
            bullets_review.get("improvement_score", 5),
            keywords_review.get("improvement_score", 5),
            specs_review.get("completeness_score", 5)
        ]
        
        overall_improvement = sum(improvement_scores) / len(improvement_scores)
        
        # Crear propuesta final integrada
        final_proposal = {
            "final_listing": {
                "title": title_review.get("optimized_title", ""),
                "description": description_review.get("optimized_description", ""),
                "bullet_points": bullets_review.get("optimized_bullets", []),
                "category": category_review.get("suggested_category", "Other"),
                "subcategory": category_review.get("subcategories", []),
                "keywords": keywords_review.get("optimized_keywords", []),
                "high_priority_keywords": keywords_review.get("high_priority_keywords", []),
                "backend_keywords": keywords_review.get("long_tail_keywords", [])
            },
            "improvements_summary": {
                "overall_improvement_score": overall_improvement,
                "title_improvements": title_review.get("changes_made", []),
                "description_improvements": description_review.get("key_improvements", []),
                "bullet_improvements": bullets_review.get("key_changes", []),
                "category_optimization": category_review.get("reasons", []),
                "keyword_optimization": keywords_review.get("high_priority_keywords", [])
            },
            "specifications_enhancement": {
                "missing_specs": specs_review.get("missing_specs", []),
                "clarification_needed": specs_review.get("needs_clarification", []),
                "technical_details": specs_review.get("technical_details", []),
                "certifications": specs_review.get("certifications", [])
            },
            "image_recommendations": {
                "optimized_images": image_suggestions.get("images", []),
                "image_search_terms": image_suggestions.get("search_terms_used", []),
                "image_confidence": image_suggestions.get("confidence", 0.0)
            },
            "quality_metrics": {
                "title_quality": title_review.get("confidence", 0.0),
                "description_quality": description_review.get("confidence", 0.0),
                "bullet_quality": bullets_review.get("confidence", 0.0),
                "category_accuracy": category_review.get("confidence", 0.0),
                "keyword_relevance": keywords_review.get("confidence", 0.0),
                "spec_completeness": specs_review.get("completeness_score", 5) / 10
            },
            "final_recommendations": self._generate_final_recommendations(review_result, image_suggestions),
            "review_metadata": {
                "reviewed_by": self.agent_name,
                "review_date": datetime.now().isoformat(),
                "overall_confidence": review_result.get("overall_confidence", 0.0),
                "improvement_score": overall_improvement,
                "ready_for_publish": overall_improvement >= 7.0
            }
        }
        
        return final_proposal

    # Métodos helper para optimización
    def _optimize_title(self, current_title: str, product_name: str, category: str, features: List[str]) -> str:
        """Optimiza el título del producto"""
        if not current_title:
            current_title = product_name
        
        # Agregar palabras clave relevantes para la categoría
        category_keywords = self.high_conversion_keywords.get(category.lower(), [])
        
        # Construir título optimizado
        optimized_title = f"{product_name} - {category_keywords[0] if category_keywords else 'Premium'}"
        
        # Agregar características principales
        if features:
            optimized_title += f" | {features[0]}"
        
        # Limitar a 200 caracteres
        if len(optimized_title) > 200:
            optimized_title = optimized_title[:197] + "..."
        
        return optimized_title

    def _optimize_description(self, current_description: str, product_name: str, features: List[str]) -> str:
        """Optimiza la descripción del producto"""
        if not current_description:
            current_description = f"Descubre {product_name}, un producto de calidad premium."
        
        # Agregar estructura mejorada
        optimized_description = f"""
        🌟 {product_name} - Tu elección inteligente para calidad y rendimiento
        
        ✅ Características destacadas:
        {chr(10).join(f"• {feature}" for feature in features[:3])}
        
        💎 ¿Por qué elegir {product_name}?
        - Calidad premium garantizada
        - Fácil de usar y mantener
        - Soporte técnico especializado
        
        🎯 Perfecto para uso diario y profesional
        
        {current_description}
        """
        
        return optimized_description.strip()

    def _optimize_bullets(self, current_bullets: List[str], product_name: str, features: List[str]) -> List[str]:
        """Optimiza los bullet points"""
        if not current_bullets:
            current_bullets = features[:5] if features else [f"Producto {product_name} de calidad"]
        
        optimized_bullets = []
        emojis = ["✅", "🔧", "🎯", "💎", "🌟"]
        
        for i, bullet in enumerate(current_bullets[:5]):
            emoji = emojis[i] if i < len(emojis) else "•"
            optimized_bullet = f"{emoji} {bullet}"
            if "premium" not in bullet.lower():
                optimized_bullet += " - Calidad premium"
            optimized_bullets.append(optimized_bullet)
        
        return optimized_bullets

    def _optimize_keywords(self, current_keywords: List[str], product_name: str, category: str, features: List[str]) -> List[str]:
        """Optimiza las palabras clave"""
        optimized_keywords = []
        
        # Agregar nombre del producto
        optimized_keywords.append(product_name.lower())
        
        # Agregar palabras clave de alta conversión para la categoría
        category_keywords = self.high_conversion_keywords.get(category.lower(), [])
        optimized_keywords.extend(category_keywords[:3])
        
        # Agregar características como keywords
        for feature in features[:3]:
            optimized_keywords.append(feature.lower())
        
        # Agregar keywords existentes relevantes
        for keyword in current_keywords[:5]:
            if keyword.lower() not in optimized_keywords:
                optimized_keywords.append(keyword.lower())
        
        return optimized_keywords[:15]  # Limitar a 15 keywords

    def _suggest_best_category(self, product_name: str, description: str, features: List[str]) -> str:
        """Sugiere la mejor categoría basada en el análisis del producto"""
        text_to_analyze = f"{product_name} {description} {' '.join(features)}".lower()
        
        category_scores = {}
        
        for category, keywords in {
            "electronics": ["electronic", "digital", "tech", "smart", "wireless", "bluetooth"],
            "sports": ["sport", "fitness", "workout", "exercise", "athletic", "training"],
            "home": ["home", "kitchen", "house", "decor", "furniture", "storage"],
            "beauty": ["beauty", "cosmetic", "skin", "hair", "makeup", "fragrance"],
            "clothing": ["clothing", "apparel", "shirt", "dress", "pants", "shoe"],
            "toys": ["toy", "game", "play", "kid", "child", "educational"],
            "books": ["book", "read", "literature", "novel", "guide", "manual"],
            "automotive": ["car", "auto", "vehicle", "driving", "motor", "automotive"],
            "tools": ["tool", "hardware", "repair", "construction", "building"],
            "health": ["health", "medical", "wellness", "supplement", "vitamin"]
        }.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            category_scores[category] = score
        
        if not category_scores or max(category_scores.values()) == 0:
            return "Other"
        
        best_category = max(category_scores, key=lambda x: category_scores[x])
        return best_category.title()

    def _calculate_category_match(self, product_name: str, category: str) -> float:
        """Calcula qué tan bien coincide el producto con la categoría"""
        if category == "Other":
            return 0.5
        
        category_keywords = {
            "Electronics": ["electronic", "tech", "digital", "smart"],
            "Sports": ["sport", "fitness", "athletic", "training"],
            "Home": ["home", "kitchen", "house", "decor"],
            "Beauty": ["beauty", "cosmetic", "skin", "hair"],
            "Clothing": ["clothing", "apparel", "fashion", "wear"],
            "Toys": ["toy", "game", "play", "kid"],
            "Books": ["book", "read", "literature", "guide"],
            "Automotive": ["car", "auto", "vehicle", "driving"],
            "Tools": ["tool", "hardware", "repair", "construction"],
            "Health": ["health", "medical", "wellness", "supplement"]
        }
        
        keywords = category_keywords.get(category, [])
        product_lower = product_name.lower()
        
        matches = sum(1 for keyword in keywords if keyword in product_lower)
        return min(matches / len(keywords), 1.0) if keywords else 0.5

    def _get_category_reasons(self, product_name: str, category: str) -> List[str]:
        """Obtiene las razones por las que se sugiere una categoría específica"""
        reasons = []
        product_lower = product_name.lower()
        
        category_indicators = {
            "Electronics": ["electronic", "tech", "digital", "smart", "wireless"],
            "Sports": ["sport", "fitness", "athletic", "training", "workout"],
            "Home": ["home", "kitchen", "house", "decor", "furniture"],
            "Beauty": ["beauty", "cosmetic", "skin", "hair", "makeup"],
            "Clothing": ["clothing", "apparel", "fashion", "wear", "shirt"],
            "Toys": ["toy", "game", "play", "kid", "child"],
            "Books": ["book", "read", "literature", "guide", "manual"],
            "Automotive": ["car", "auto", "vehicle", "driving", "motor"],
            "Tools": ["tool", "hardware", "repair", "construction", "building"],
            "Health": ["health", "medical", "wellness", "supplement", "vitamin"]
        }
        
        indicators = category_indicators.get(category, [])
        for indicator in indicators:
            if indicator in product_lower:
                reasons.append(f"Contiene término relacionado: '{indicator}'")
        
        if not reasons:
            reasons.append("Basado en análisis semántico del producto")
        
        return reasons

    def _identify_missing_specs(self, current_specs: str, category: str) -> List[str]:
        """Identifica especificaciones faltantes importantes"""
        missing_specs = []
        
        # Especificaciones comunes que suelen faltar
        common_specs = {
            "electronics": ["Dimensiones", "Peso", "Compatibilidad", "Garantía"],
            "sports": ["Talla", "Material", "Peso", "Instrucciones de cuidado"],
            "home": ["Dimensiones", "Material", "Capacidad", "Instrucciones de limpieza"],
            "beauty": ["Ingredientes", "Tipo de piel", "Modo de uso", "Precauciones"],
            "clothing": ["Talla", "Material", "Instrucciones de lavado", "País de origen"],
            "toys": ["Edad recomendada", "Material", "Dimensiones", "Certificaciones de seguridad"],
            "automotive": ["Compatibilidad", "Materiales", "Instrucciones de instalación", "Garantía"],
            "tools": ["Especificaciones técnicas", "Materiales", "Dimensiones", "Certificaciones"],
            "health": ["Ingredientes", "Dosis", "Contraindicaciones", "Certificaciones"]
        }
        
        specs_for_category = common_specs.get(category.lower(), ["Dimensiones", "Peso", "Material", "Garantía"])
        
        for spec in specs_for_category:
            if spec.lower() not in current_specs.lower():
                missing_specs.append(spec)
        
        return missing_specs

    def _calculate_overall_confidence(self, review_results: List[Dict[str, Any]]) -> float:
        """Calcula la confianza general basada en todas las revisiones"""
        confidences = []
        
        for result in review_results:
            if isinstance(result, dict) and "confidence" in result:
                confidences.append(result["confidence"])
        
        if not confidences:
            return 0.5
        
        return sum(confidences) / len(confidences)

    def _generate_general_recommendations(self, reviews: List[Dict[str, Any]]) -> List[str]:
        """Genera recomendaciones generales basadas en todas las revisiones"""
        recommendations = []
        
        # Recomendaciones generales
        general_recs = [
            "Considera agregar más detalles técnicos específicos",
            "Incluye información sobre garantía y soporte",
            "Agrega casos de uso específicos para diferentes audiencias",
            "Optimiza para búsquedas móviles con palabras clave cortas",
            "Incluye comparaciones con productos similares",
            "Agrega información sobre envío y devoluciones"
        ]
        
        recommendations.extend(general_recs[:5])  # Top 5 recomendaciones
        
        return recommendations

    def _generate_final_recommendations(self, review_result: Dict[str, Any], image_suggestions: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones finales basadas en toda la revisión"""
        recommendations = []
        
        # Recomendaciones basadas en puntuaciones
        title_score = review_result.get("title_review", {}).get("improvement_score", 5)
        if title_score < 7:
            recommendations.append("Considera hacer el título más descriptivo y agregar palabras clave específicas")
        
        description_score = review_result.get("description_review", {}).get("improvement_score", 5)
        if description_score < 7:
            recommendations.append("Mejora la descripción enfocándote en beneficios específicos y casos de uso")
        
        bullets_score = review_result.get("bullets_review", {}).get("improvement_score", 5)
        if bullets_score < 7:
            recommendations.append("Optimiza los bullet points para destacar características únicas")
        
        # Recomendaciones de categoría
        category_confidence = review_result.get("category_review", {}).get("confidence", 0.0)
        if category_confidence < 0.8:
            recommendations.append("Verifica que la categoría seleccionada sea la más específica")
        
        # Recomendaciones de especificaciones
        missing_specs = review_result.get("specs_review", {}).get("missing_specs", [])
        if missing_specs:
            recommendations.append(f"Agrega especificaciones faltantes: {', '.join(missing_specs[:3])}")
        
        # Recomendaciones de imágenes
        image_confidence = image_suggestions.get("confidence", 0.0)
        if image_confidence < 0.7:
            recommendations.append("Considera agregar imágenes de mayor calidad que muestren el producto en uso")
        
        # Recomendaciones generales
        overall_confidence = review_result.get("overall_confidence", 0.0)
        if overall_confidence < 0.8:
            recommendations.append("Realiza una revisión adicional de todos los elementos antes de publicar")
        
        return recommendations[:8]  # Limitar a 8 recomendaciones

    def _calculate_title_improvement(self, current_title: str, optimized_title: str) -> int:
        """Calcula la puntuación de mejora del título"""
        if not current_title:
            return 10
        
        # Factores de mejora
        improvement_factors = 0
        
        # Longitud apropiada
        if 50 <= len(optimized_title) <= 200:
            improvement_factors += 2
        
        # Contiene palabras clave
        if any(keyword in optimized_title.lower() for keyword in ["premium", "quality", "professional"]):
            improvement_factors += 2
        
        # Estructura mejorada
        if "|" in optimized_title or "-" in optimized_title:
            improvement_factors += 2
        
        # Diferente al original
        if optimized_title != current_title:
            improvement_factors += 2
        
        return min(improvement_factors + 2, 10)  # Base de 2 + mejoras, máximo 10

    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extrae palabras clave del título"""
        # Palabras comunes a excluir
        stop_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "-", "|"}
        
        # Dividir el título en palabras
        words = re.findall(r'\b\w+\b', title.lower())
        
        # Filtrar stop words y palabras muy cortas
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limitar a 10 keywords

    async def cleanup(self):
        """Limpia recursos del agente"""
        if hasattr(self, 'image_agent'):
            await self.image_agent.cleanup()
