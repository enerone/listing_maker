"""
Marketing Review Agent - Especialista en Marketing Digital
=====================================================

Este agente se especializa en revisar listings desde una perspectiva de marketing digital,
analizando aspectos como conversión, persuasión, SEO, psicología del consumidor y optimización para ventas.
"""

import json
import logging
from typing import Dict, Any
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

ANÁLISIS REQUERIDO (escala 1-10):

{{
    "analisis_marketing": {{
        "persuasion_conversion": {{
            "puntuacion": 0,
            "fortalezas": [""],
            "debilidades": [""],
            "oportunidades": [""]
        }},
        "psicologia_consumidor": {{
            "puntuacion": 0,
            "triggers_usados": [""],
            "triggers_faltantes": [""],
            "conexion_emocional": 0
        }},
        "seo_visibilidad": {{
            "puntuacion": 0,
            "keywords_efectivas": [""],
            "keywords_faltantes": [""],
            "densidad_optima": true
        }},
        "estructura_ventas": {{
            "puntuacion": 0,
            "sigue_framework": "",
            "jerarquia_correcta": true,
            "cta_presente": true
        }},
        "diferenciacion": {{
            "puntuacion": 0,
            "ventajas_claras": true,
            "propuesta_valor": "",
            "justifica_precio": true
        }},
        "mobile_optimization": {{
            "puntuacion": 0,
            "titulo_mobile_friendly": true,
            "bullets_escaneables": true,
            "info_clave_arriba": true
        }}
    }},
    "mejoras_recomendadas": {{
        "titulo_optimizado": {{
            "nuevo_titulo": "",
            "cambios_realizados": [""],
            "razonamiento": ""
        }},
        "descripcion_mejorada": {{
            "nueva_descripcion": "",
            "estructura_usada": "",
            "elementos_persuasivos": [""],
            "storytelling_aplicado": ""
        }},
        "bullet_points_optimizados": [
            {{
                "bullet": "",
                "tipo_beneficio": "",
                "trigger_psicologico": ""
            }}
        ],
        "keywords_adicionales": {{
            "alta_conversion": [""],
            "long_tail": [""],
            "semanticas": [""]
        }},
        "estrategia_precio": {{
            "analisis_actual": "",
            "recomendacion": "",
            "posicionamiento_sugerido": ""
        }}
    }},
    "puntuacion_general": 0,
    "prioridades_implementacion": [""],
    "impacto_esperado": {{
        "conversion_rate": "",
        "visibilidad_seo": "",
        "diferenciacion": ""
    }},
    "recomendaciones_adicionales": [""],
    "confidence_score": 0.0
}}
"""
    
    def _create_fallback_result(self, product_data: Dict[str, Any], listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera el prompt para el análisis de marketing digital del listing.
        """
        current_title = listing_data.get('title', '')
        current_description = listing_data.get('description', '')
        current_bullet_points = listing_data.get('bullet_points', [])
        current_keywords = listing_data.get('keywords', [])
        target_price = listing_data.get('target_price', 0)
        
        prompt = f"""
Eres un experto en MARKETING DIGITAL y OPTIMIZACIÓN DE CONVERSIONES con más de 10 años de experiencia en e-commerce y Amazon. 

Tu misión es revisar este listing desde una perspectiva de marketing digital para maximizar las ventas y conversiones.

INFORMACIÓN DEL PRODUCTO:
Nombre: {product_data.get('product_name', 'N/A')}
Categoría: {product_data.get('category', 'N/A')}
Características: {', '.join(product_data.get('features', []))}
Precio objetivo: ${target_price}

LISTING ACTUAL A REVISAR:
Título: {current_title}
Descripción: {current_description}
Bullet Points: {json.dumps(current_bullet_points, ensure_ascii=False)}
Keywords: {', '.join(current_keywords)}

ANÁLISIS REQUERIDO - Evalúa cada aspecto del 1 al 10:

1. PERSUASIÓN Y CONVERSIÓN:
   - ¿El título genera urgencia/deseo?
   - ¿Los beneficios emocionales están claros?
   - ¿Hay elementos de escasez/urgencia?
   - ¿Se aborda la objeción principal del cliente?

2. PSICOLOGÍA DEL CONSUMIDOR:
   - ¿Se conecta con el dolor/necesidad del cliente?
   - ¿Usa triggers psicológicos efectivos?
   - ¿El lenguaje es aspiracional?
   - ¿Genera confianza y credibilidad?

3. SEO Y VISIBILIDAD:
   - ¿Las keywords están bien distribuidas?
   - ¿El título es search-friendly?
   - ¿Hay long-tail keywords relevantes?
   - ¿La densidad de keywords es óptima?

4. ESTRUCTURA DE VENTAS:
   - ¿Sigue una estructura persuasiva (AIDA, PAS, etc.)?
   - ¿Los bullet points priorizan beneficios sobre características?
   - ¿Hay un call-to-action implícito?
   - ¿La jerarquía de información es correcta?

5. DIFERENCIACIÓN COMPETITIVA:
   - ¿Se destaca claramente vs competencia?
   - ¿Hay una propuesta de valor única?
   - ¿Se mencionan ventajas competitivas?
   - ¿Justifica el precio?

6. OPTIMIZACIÓN PARA MÓVIL:
   - ¿El título se lee bien truncado?
   - ¿Los bullet points son escaneables?
   - ¿La información clave está al inicio?
   - ¿Es mobile-friendly?

MEJORAS ESPECÍFICAS - Proporciona:

1. TÍTULO OPTIMIZADO:
   - Versión mejorada con mayor poder de conversión
   - Explicación de cambios

2. DESCRIPCIÓN MEJORADA:
   - Versión optimizada con estructura de ventas
   - Uso de storytelling y triggers psicológicos

3. BULLET POINTS MEJORADOS:
   - 5 bullet points optimizados para conversión
   - Enfoque en beneficios emocionales y racionales

4. KEYWORDS ADICIONALES:
   - Keywords de alta conversión no incluidas
   - Long-tail keywords específicas

5. ESTRATEGIAS DE PRECIO:
   - Análisis del precio actual
   - Recomendaciones de posicionamiento

FORMATO DE RESPUESTA:
Responde SOLO en formato JSON válido:

{{
    "analisis_marketing": {{
        "persuasion_conversion": {{
            "puntuacion": 0,
            "fortalezas": [""],
            "debilidades": [""],
            "oportunidades": [""]
        }},
        "psicologia_consumidor": {{
            "puntuacion": 0,
            "triggers_usados": [""],
            "triggers_faltantes": [""],
            "conexion_emocional": 0
        }},
        "seo_visibilidad": {{
            "puntuacion": 0,
            "keywords_efectivas": [""],
            "keywords_faltantes": [""],
            "densidad_optima": true
        }},
        "estructura_ventas": {{
            "puntuacion": 0,
            "sigue_framework": "",
            "jerarquia_correcta": true,
            "cta_presente": true
        }},
        "diferenciacion": {{
            "puntuacion": 0,
            "ventajas_claras": true,
            "propuesta_valor": "",
            "justifica_precio": true
        }},
        "mobile_optimization": {{
            "puntuacion": 0,
            "titulo_mobile_friendly": true,
            "bullets_escaneables": true,
            "info_clave_arriba": true
        }}
    }},
    "mejoras_recomendadas": {{
        "titulo_optimizado": {{
            "nuevo_titulo": "",
            "cambios_realizados": [""],
            "razonamiento": ""
        }},
        "descripcion_mejorada": {{
            "nueva_descripcion": "",
            "estructura_usada": "",
            "elementos_persuasivos": [""],
            "storytelling_aplicado": ""
        }},
        "bullet_points_optimizados": [
            {{
                "bullet": "",
                "tipo_beneficio": "",
                "trigger_psicologico": ""
            }}
        ],
        "keywords_adicionales": {{
            "alta_conversion": [""],
            "long_tail": [""],
            "semanticas": [""]
        }},
        "estrategia_precio": {{
            "analisis_actual": "",
            "recomendacion": "",
            "posicionamiento_sugerido": ""
        }}
    }},
    "puntuacion_general": 0,
    "prioridades_implementacion": [""],
    "impacto_esperado": {{
        "conversion_rate": "",
        "visibilidad_seo": "",
        "diferenciacion": ""
    }},
    "recomendaciones_adicionales": [""],
    "confidence_score": 0.0
}}

IMPORTANTE:
- Sé específico y práctico en las recomendaciones
- Enfócate en elementos que realmente impacten las ventas
- Considera el público objetivo y la categoría del producto
- Prioriza cambios de alto impacto y fácil implementación
- Usa principios de marketing digital comprobados
- Responde ÚNICAMENTE en formato JSON válido, sin texto adicional
"""
        
        return prompt
    
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
                
                return {
                    "success": True,
                    "agent_name": self.agent_name,
                    "data": analysis_data,
                    "confidence": analysis_data.get("confidence_score", 0.7),
                    "processing_time": response["processing_time"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback si no se pudo parsear
                return self._create_fallback_result(product_data, listing_data)
                
        except Exception as e:
            logger.error(f"Error en análisis de marketing: {str(e)}")
            return {
                "success": False,
                "agent_name": self.agent_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_listing_data(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae los datos del listing de resultados previos.
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
        
        # Buscar en diferentes agentes
        agents_to_check = [
            'ProductDescriptionAgent',
            'ContentAgent', 
            'SEOVisualAgent',
            'ValuePropositionAgent'
        ]
        
        for agent_name in agents_to_check:
            agent_result = previous_results.get(agent_name, {})
            
            # Extraer título
            if not listing_data['title'] and 'titulo' in agent_result:
                listing_data['title'] = agent_result['titulo']
            elif not listing_data['title'] and 'title' in agent_result:
                listing_data['title'] = agent_result['title']
            
            # Extraer descripción
            if not listing_data['description'] and 'descripcion' in agent_result:
                listing_data['description'] = agent_result['descripcion']
            elif not listing_data['description'] and 'description' in agent_result:
                listing_data['description'] = agent_result['description']
            
            # Extraer bullet points
            if not listing_data['bullet_points'] and 'bullet_points' in agent_result:
                listing_data['bullet_points'] = agent_result['bullet_points']
            elif not listing_data['bullet_points'] and 'puntos_clave' in agent_result:
                listing_data['bullet_points'] = agent_result['puntos_clave']
            
            # Extraer keywords
            if 'keywords' in agent_result:
                if isinstance(agent_result['keywords'], list):
                    listing_data['keywords'].extend(agent_result['keywords'])
                
            # Extraer precio
            if 'target_price' in agent_result:
                listing_data['target_price'] = agent_result['target_price']
        
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
            
            # Agregar métricas de texto
            titulo = listing_data.get('title', '')
            descripcion = listing_data.get('description', '')
            
            result['metricas_texto'] = {
                'longitud_titulo': len(titulo),
                'longitud_titulo_optima': 150 <= len(titulo) <= 200,
                'palabras_titulo': len(titulo.split()) if titulo else 0,
                'longitud_descripcion': len(descripcion),
                'palabras_descripcion': len(descripcion.split()) if descripcion else 0,
                'densidad_keywords': self._calculate_keyword_density(listing_data)
            }
            
            # Asegurar confidence_score
            if 'confidence_score' not in result or result['confidence_score'] == 0:
                result['confidence_score'] = min(0.9, result.get('puntuacion_general', 0) / 10)
            
        except Exception as e:
            logger.error(f"Error calculando métricas adicionales: {e}")
        
        return result
    
    def _calculate_keyword_density(self, listing_data: Dict[str, Any]) -> float:
        """
        Calcula la densidad de keywords en el texto.
        """
        try:
            texto_completo = ' '.join([
                listing_data.get('title', ''),
                listing_data.get('description', ''),
                ' '.join(listing_data.get('bullet_points', []))
            ]).lower()
            
            if not texto_completo:
                return 0.0
            
            keywords = listing_data.get('keywords', [])
            if not keywords:
                return 0.0
            
            total_palabras = len(texto_completo.split())
            keyword_occurrences = 0
            
            for keyword in keywords:
                keyword_occurrences += texto_completo.count(keyword.lower())
            
            return round((keyword_occurrences / total_palabras) * 100, 2) if total_palabras > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida y limpia el resultado del análisis.
        """
        # Estructura base requerida
        base_structure = {
            'analisis_marketing': {
                'persuasion_conversion': {'puntuacion': 5, 'fortalezas': [], 'debilidades': [], 'oportunidades': []},
                'psicologia_consumidor': {'puntuacion': 5, 'triggers_usados': [], 'triggers_faltantes': [], 'conexion_emocional': 5},
                'seo_visibilidad': {'puntuacion': 5, 'keywords_efectivas': [], 'keywords_faltantes': [], 'densidad_optima': True},
                'estructura_ventas': {'puntuacion': 5, 'sigue_framework': '', 'jerarquia_correcta': True, 'cta_presente': True},
                'diferenciacion': {'puntuacion': 5, 'ventajas_claras': True, 'propuesta_valor': '', 'justifica_precio': True},
                'mobile_optimization': {'puntuacion': 5, 'titulo_mobile_friendly': True, 'bullets_escaneables': True, 'info_clave_arriba': True}
            },
            'mejoras_recomendadas': {
                'titulo_optimizado': {'nuevo_titulo': '', 'cambios_realizados': [], 'razonamiento': ''},
                'descripcion_mejorada': {'nueva_descripcion': '', 'estructura_usada': '', 'elementos_persuasivos': [], 'storytelling_aplicado': ''},
                'bullet_points_optimizados': [],
                'keywords_adicionales': {'alta_conversion': [], 'long_tail': [], 'semanticas': []},
                'estrategia_precio': {'analisis_actual': '', 'recomendacion': '', 'posicionamiento_sugerido': ''}
            },
            'puntuacion_general': 5,
            'prioridades_implementacion': [],
            'impacto_esperado': {'conversion_rate': '', 'visibilidad_seo': '', 'diferenciacion': ''},
            'recomendaciones_adicionales': [],
            'confidence_score': 0.5
        }
        
        # Mergear con estructura base
        return self._deep_merge(base_structure, result)
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Hace un merge profundo de diccionarios.
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Crea un resultado de error estándar.
        """
        return {
            'agent_name': self.agent_name,
            'error': True,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'analisis_marketing': {
                'persuasion_conversion': {'puntuacion': 0, 'fortalezas': [], 'debilidades': ['Error en análisis'], 'oportunidades': []},
                'psicologia_consumidor': {'puntuacion': 0, 'triggers_usados': [], 'triggers_faltantes': [], 'conexion_emocional': 0},
                'seo_visibilidad': {'puntuacion': 0, 'keywords_efectivas': [], 'keywords_faltantes': [], 'densidad_optima': False},
                'estructura_ventas': {'puntuacion': 0, 'sigue_framework': '', 'jerarquia_correcta': False, 'cta_presente': False},
                'diferenciacion': {'puntuacion': 0, 'ventajas_claras': False, 'propuesta_valor': '', 'justifica_precio': False},
                'mobile_optimization': {'puntuacion': 0, 'titulo_mobile_friendly': False, 'bullets_escaneables': False, 'info_clave_arriba': False}
            },
            'mejoras_recomendadas': {
                'titulo_optimizado': {'nuevo_titulo': '', 'cambios_realizados': [], 'razonamiento': 'Error en análisis'},
                'descripcion_mejorada': {'nueva_descripcion': '', 'estructura_usada': '', 'elementos_persuasivos': [], 'storytelling_aplicado': ''},
                'bullet_points_optimizados': [],
                'keywords_adicionales': {'alta_conversion': [], 'long_tail': [], 'semanticas': []},
                'estrategia_precio': {'analisis_actual': '', 'recomendacion': '', 'posicionamiento_sugerido': ''}
            },
            'puntuacion_general': 0,
            'prioridades_implementacion': ['Resolver errores técnicos'],
            'impacto_esperado': {'conversion_rate': 'N/A', 'visibilidad_seo': 'N/A', 'diferenciacion': 'N/A'},
            'recomendaciones_adicionales': ['Revisar configuración del agente'],
            'confidence_score': 0.0
        }
