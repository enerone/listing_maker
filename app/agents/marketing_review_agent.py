"""
Marketing Review Agent - Especialista en Marketing Digital
=====================================================

Este agente se especializa en revisar listings desde una perspectiva de marketing digital,
analizando aspectos como conversión, persuasión, SEO, psicología del consumidor y optimización para ventas.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MarketingReviewAgent(BaseAgent):
    """
    Agente especialista en marketing digital que revisa y optimiza listings
    desde una perspectiva de conversión y ventas.
    """
    
    def __init__(self):
        super().__init__("MarketingReviewAgent", temperature=0.4)
        
    def get_system_prompt(self) -> str:
        return """
        Eres un experto en MARKETING DIGITAL y OPTIMIZACIÓN DE CONVERSIONES con más de 10 años de experiencia en e-commerce y Amazon.
        
        Tu misión es revisar listings desde una perspectiva de marketing digital para maximizar las ventas y conversiones.
        
        Debes analizar persuasión, psicología del consumidor, SEO, estructura de ventas, diferenciación competitiva y optimización móvil.
        
        IMPORTANTE: Responde únicamente con un objeto JSON válido sin texto adicional.
        """

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa el listing actual y genera un análisis de marketing digital.
        """
        try:
            # Extraer datos del listing de resultados previos
            listing_data = self._extract_listing_data(data.get('previous_results', {}))
            product_data = data.get('product_data', {})
            
            # Construir prompt específico
            prompt = self._build_analysis_prompt(product_data, listing_data)
            
            # Generar respuesta estructurada usando el método base
            response = await self._generate_response(prompt, structured=True)
            
            if response["success"] and response.get("is_structured", False):
                # Procesar datos parseados
                analysis_data = response["parsed_data"]
                analysis_data = self._calculate_additional_metrics(analysis_data, listing_data)
                
                # Extraer recomendaciones de los datos de análisis
                recommendations = self._extract_recommendations_from_analysis(analysis_data)
                
                return {
                    "success": True,
                    "agent_name": self.agent_name,
                    "data": analysis_data,
                    "confidence": analysis_data.get("confidence_score", 0.7),
                    "processing_time": response["processing_time"],
                    "recommendations": recommendations,
                    "notes": [f"Puntuación de marketing: {analysis_data.get('puntuacion_general', 0)}/10"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback si no se pudo parsear
                fallback_result = self._create_fallback_result(product_data, listing_data)
                fallback_result["recommendations"] = [
                    "Análisis automático limitado - revisar manualmente",
                    "Optimizar título para mejor visibilidad",
                    "Mejorar descripción con elementos persuasivos"
                ]
                fallback_result["notes"] = ["Análisis de fallback aplicado"]
                return fallback_result
                
        except Exception as e:
            logger.error(f"Error en análisis de marketing: {str(e)}")
            return {
                "success": False,
                "agent_name": self.agent_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _build_analysis_prompt(self, product_data: Dict[str, Any], listing_data: Dict[str, Any]) -> str:
        """
        Construye el prompt para el análisis de marketing digital.
        """
        current_title = listing_data.get('title', '')
        current_description = listing_data.get('description', '')
        current_bullet_points = listing_data.get('bullet_points', [])
        current_keywords = listing_data.get('keywords', [])
        target_price = listing_data.get('target_price', 0)
        
        return f"""
Analiza este listing desde una perspectiva de MARKETING DIGITAL para maximizar conversiones:

PRODUCTO:
Nombre: {product_data.get('product_name', 'N/A')}
Categoría: {product_data.get('category', 'N/A')}
Características: {', '.join(product_data.get('features', []))}
Precio: ${target_price}

LISTING ACTUAL:
Título: {current_title}
Descripción: {current_description}
Bullet Points: {json.dumps(current_bullet_points, ensure_ascii=False)}
Keywords: {', '.join(current_keywords)}

Proporciona análisis detallado en formato JSON con:
- Análisis de persuasión y conversión (puntuación 1-10)
- Psicología del consumidor aplicada
- SEO y visibilidad
- Estructura de ventas
- Diferenciación competitiva  
- Optimización móvil
- Mejoras recomendadas específicas
- Puntuación general y nivel de confianza

{{
    "analisis_marketing": {{
        "persuasion_conversion": {{"puntuacion": 0, "fortalezas": [], "debilidades": [], "oportunidades": []}},
        "psicologia_consumidor": {{"puntuacion": 0, "triggers_usados": [], "triggers_faltantes": [], "conexion_emocional": 0}},
        "seo_visibilidad": {{"puntuacion": 0, "keywords_efectivas": [], "keywords_faltantes": [], "densidad_optima": true}},
        "estructura_ventas": {{"puntuacion": 0, "sigue_framework": "", "jerarquia_correcta": true, "cta_presente": true}},
        "diferenciacion": {{"puntuacion": 0, "ventajas_claras": true, "propuesta_valor": "", "justifica_precio": true}},
        "mobile_optimization": {{"puntuacion": 0, "titulo_mobile_friendly": true, "bullets_escaneables": true, "info_clave_arriba": true}}
    }},
    "mejoras_recomendadas": {{
        "titulo_optimizado": {{"nuevo_titulo": "", "cambios_realizados": [], "razonamiento": ""}},
        "descripcion_mejorada": {{"nueva_descripcion": "", "estructura_usada": "", "elementos_persuasivos": [], "storytelling_aplicado": ""}},
        "bullet_points_optimizados": [{{"bullet": "", "tipo_beneficio": "", "trigger_psicologico": ""}}],
        "keywords_adicionales": {{"alta_conversion": [], "long_tail": [], "semanticas": []}},
        "estrategia_precio": {{"analisis_actual": "", "recomendacion": "", "posicionamiento_sugerido": ""}}
    }},
    "puntuacion_general": 0,
    "prioridades_implementacion": [],
    "impacto_esperado": {{"conversion_rate": "", "visibilidad_seo": "", "diferenciacion": ""}},
    "recomendaciones_adicionales": [],
    "confidence_score": 0.0
}}
"""
    
    def _create_fallback_result(self, product_data: Dict[str, Any], listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un resultado de fallback cuando no se puede analizar automáticamente.
        """
        return {
            "success": True,
            "agent_name": self.agent_name,
            "data": {
                "analisis_marketing": {
                    "persuasion_conversion": {"puntuacion": 5, "fortalezas": [], "debilidades": ["Análisis manual requerido"], "oportunidades": []},
                    "psicologia_consumidor": {"puntuacion": 5, "triggers_usados": [], "triggers_faltantes": [], "conexion_emocional": 5},
                    "seo_visibilidad": {"puntuacion": 5, "keywords_efectivas": [], "keywords_faltantes": [], "densidad_optima": True},
                    "estructura_ventas": {"puntuacion": 5, "sigue_framework": "AIDA", "jerarquia_correcta": True, "cta_presente": True},
                    "diferenciacion": {"puntuacion": 5, "ventajas_claras": True, "propuesta_valor": "Por definir", "justifica_precio": True},
                    "mobile_optimization": {"puntuacion": 5, "titulo_mobile_friendly": True, "bullets_escaneables": True, "info_clave_arriba": True}
                },
                "mejoras_recomendadas": {
                    "titulo_optimizado": {"nuevo_titulo": listing_data.get('title', ''), "cambios_realizados": [], "razonamiento": "Revisar manualmente"},
                    "descripcion_mejorada": {"nueva_descripcion": listing_data.get('description', ''), "estructura_usada": "", "elementos_persuasivos": [], "storytelling_aplicado": ""},
                    "bullet_points_optimizados": [],
                    "keywords_adicionales": {"alta_conversion": [], "long_tail": [], "semanticas": []},
                    "estrategia_precio": {"analisis_actual": "Por revisar", "recomendacion": "Análisis competitivo", "posicionamiento_sugerido": "Premium"}
                },
                "puntuacion_general": 5,
                "prioridades_implementacion": ["Análisis manual detallado"],
                "impacto_esperado": {"conversion_rate": "Por determinar", "visibilidad_seo": "Por determinar", "diferenciacion": "Por determinar"},
                "recomendaciones_adicionales": ["Revisar competencia", "Optimizar keywords", "Mejorar estructura"],
                "confidence_score": 0.5
            },
            "confidence": 0.5,
            "processing_time": 0.1,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_listing_data(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae los datos del listing de resultados previos de otros agentes.
        """
        listing_data = {
            'title': '',
            'description': '',
            'bullet_points': [],
            'keywords': [],
            'target_price': 0
        }
        
        if not previous_results:
            return listing_data
        
        # Buscar en diferentes agentes (simplificado)
        for agent_result in previous_results.values():
            if isinstance(agent_result, dict):
                # Título
                if not listing_data['title']:
                    listing_data['title'] = agent_result.get('titulo', agent_result.get('title', ''))
                
                # Descripción
                if not listing_data['description']:
                    listing_data['description'] = agent_result.get('descripcion', agent_result.get('description', ''))
                
                # Bullet points
                if not listing_data['bullet_points']:
                    listing_data['bullet_points'] = agent_result.get('bullet_points', agent_result.get('puntos_clave', []))
                
                # Keywords
                keywords = agent_result.get('keywords', [])
                if isinstance(keywords, list):
                    listing_data['keywords'].extend(keywords)
                
                # Precio
                if not listing_data['target_price']:
                    listing_data['target_price'] = agent_result.get('target_price', 0)
        
        return listing_data
    
    def _calculate_additional_metrics(self, result: Dict[str, Any], listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula métricas adicionales de marketing.
        """
        try:
            # Calcular puntuación general si no está presente
            if 'puntuacion_general' not in result or result['puntuacion_general'] == 0:
                analisis = result.get('analisis_marketing', {})
                puntuaciones = []
                
                for categoria in analisis.values():
                    if isinstance(categoria, dict) and 'puntuacion' in categoria:
                        puntuaciones.append(categoria['puntuacion'])
                
                if puntuaciones:
                    result['puntuacion_general'] = round(sum(puntuaciones) / len(puntuaciones), 1)
            
            # Asegurar confidence_score
            if 'confidence_score' not in result or result['confidence_score'] == 0:
                result['confidence_score'] = min(0.9, result.get('puntuacion_general', 0) / 10)
            
        except Exception as e:
            logger.error(f"Error calculando métricas adicionales: {e}")
        
        return result
    
    def _extract_recommendations_from_analysis(self, analysis_data: Dict[str, Any]) -> List[str]:
        """
        Extrae recomendaciones específicas del análisis de marketing.
        """
        recommendations = []
        
        try:
            # Extraer de recomendaciones adicionales
            if 'recomendaciones_adicionales' in analysis_data:
                adicionales = analysis_data['recomendaciones_adicionales']
                if isinstance(adicionales, list):
                    recommendations.extend(adicionales)
            
            # Extraer de mejoras recomendadas
            mejoras = analysis_data.get('mejoras_recomendadas', {})
            
            # Título optimizado
            if 'titulo_optimizado' in mejoras:
                titulo_data = mejoras['titulo_optimizado']
                if isinstance(titulo_data, dict) and titulo_data.get('cambios_realizados'):
                    cambios = titulo_data['cambios_realizados']
                    if isinstance(cambios, list) and cambios:
                        recommendations.append(f"Optimizar título: {', '.join(cambios[:2])}")
            
            # Keywords adicionales
            if 'keywords_adicionales' in mejoras:
                keywords_data = mejoras['keywords_adicionales']
                if isinstance(keywords_data, dict):
                    total_keywords = 0
                    for categoria in ['alta_conversion', 'long_tail', 'semanticas']:
                        if categoria in keywords_data and isinstance(keywords_data[categoria], list):
                            total_keywords += len(keywords_data[categoria])
                    
                    if total_keywords > 0:
                        recommendations.append(f"Incorporar {total_keywords} keywords adicionales para mejor SEO")
            
            # Análisis de categorías con puntuación baja
            analisis = analysis_data.get('analisis_marketing', {})
            for categoria, datos in analisis.items():
                if isinstance(datos, dict) and datos.get('puntuacion', 10) < 7:
                    categoria_nombre = categoria.replace('_', ' ').title()
                    debilidades = datos.get('debilidades', [])
                    if debilidades and isinstance(debilidades, list):
                        recommendations.append(f"Mejorar {categoria_nombre}: {debilidades[0]}")
            
            # Prioridades de implementación
            if 'prioridades_implementacion' in analysis_data:
                prioridades = analysis_data['prioridades_implementacion']
                if isinstance(prioridades, list) and prioridades:
                    recommendations.append(f"Prioridad alta: {prioridades[0]}")
            
            # Puntuación general baja
            puntuacion = analysis_data.get('puntuacion_general', 10)
            if puntuacion < 6:
                recommendations.append("Revisar estrategia de marketing general - puntuación por debajo del promedio")
            
            # Limitar a máximo 5 recomendaciones más relevantes
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error extrayendo recomendaciones: {e}")
            return ["Revisar análisis de marketing completo en datos del agente"]
