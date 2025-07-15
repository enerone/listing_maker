#!/usr/bin/env python3
"""
Prueba directa del MarketingReviewAgent para verificar su funcionamiento
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.marketing_review_agent import MarketingReviewAgent

async def test_marketing_agent():
    print('=== PRUEBA DIRECTA DEL MARKETING REVIEW AGENT ===')
    
    try:
        agent = MarketingReviewAgent()
        print('✅ MarketingReviewAgent instanciado correctamente')
        
        # Datos de prueba completos
        test_data = {
            'product_data': {
                'product_name': 'Termo Acero Inoxidable',
                'category': 'Home & Kitchen',
                'features': ['Acero inoxidable', 'Aislamiento térmico', 'Diseño ergonómico'],
                'target_price': 45.0,
                'target_audience': 'Deportistas y personas activas',
                'use_cases': ['Deportes', 'Oficina', 'Viajes']
            },
            'previous_results': {
                'content': {
                    'title': 'TechPro Termo Acero Inoxidable para Deportistas - Ligero y Resistente',
                    'description': 'Termo perfecto para deportistas con acero inoxidable de alta calidad. Mantiene las bebidas calientes por 12 horas y frías por 24 horas.',
                    'bullet_points': [
                        'Diseñado para deportistas y personas activas',
                        'Acero inoxidable de alta calidad con doble pared',
                        'Mantiene temperatura por hasta 24 horas',
                        'Diseño ergonómico y antideslizante',
                        'Libre de BPA y materiales tóxicos'
                    ],
                    'keywords': ['termo', 'acero', 'deportistas', 'inoxidable', 'aislamiento']
                },
                'pricing': {
                    'recommended_price': 45.0,
                    'competitive_position': 'Premium'
                },
                'seo': {
                    'search_terms': ['termo deportivo', 'botella acero inoxidable', 'termo viaje'],
                    'backend_keywords': ['deportes', 'fitness', 'hidratación', 'portable']
                }
            }
        }
        
        print('🔄 Ejecutando MarketingReviewAgent...')
        result = await agent.process(test_data)
        
        print(f'\n📊 RESULTADOS DEL AGENTE:')
        print(f'   - Éxito: {result.get("success", False)}')
        print(f'   - Confianza: {result.get("confidence", "N/A")}')
        print(f'   - Tiempo de procesamiento: {result.get("processing_time", "N/A")}s')
        
        if result.get('success') and 'data' in result:
            print('\n🔍 ANÁLISIS GENERADO:')
            data = result['data']
            
            # Mostrar análisis de conversión
            if 'conversion_analysis' in data:
                print(f'   📈 Análisis de Conversión:')
                conversion = data['conversion_analysis']
                if isinstance(conversion, dict):
                    for key, value in conversion.items():
                        print(f'      - {key}: {value}')
                else:
                    print(f'      - {conversion}')
            
            # Mostrar score de marketing
            if 'marketing_score' in data:
                print(f'   📊 Marketing Score: {data["marketing_score"]}')
            
            # Mostrar recomendaciones
            if 'recommendations' in data:
                print(f'   💡 Recomendaciones:')
                recommendations = data['recommendations']
                if isinstance(recommendations, list):
                    for i, rec in enumerate(recommendations, 1):
                        print(f'      {i}. {rec}')
                else:
                    print(f'      - {recommendations}')
            
            # Mostrar análisis competitivo
            if 'competitive_analysis' in data:
                print(f'   🎯 Análisis Competitivo:')
                competitive = data['competitive_analysis']
                if isinstance(competitive, dict):
                    for key, value in competitive.items():
                        print(f'      - {key}: {value}')
                else:
                    print(f'      - {competitive}')
            
            # Mostrar optimizaciones
            if 'optimization_suggestions' in data:
                print(f'   ⚡ Sugerencias de Optimización:')
                optimizations = data['optimization_suggestions']
                if isinstance(optimizations, list):
                    for i, opt in enumerate(optimizations, 1):
                        print(f'      {i}. {opt}')
                else:
                    print(f'      - {optimizations}')
        
        # Mostrar recomendaciones a nivel de resultado
        if 'recommendations' in result:
            print(f'\n🎯 RECOMENDACIONES DEL AGENTE:')
            for i, rec in enumerate(result['recommendations'], 1):
                print(f'   {i}. {rec}')
        
        # Mostrar notas adicionales
        if 'notes' in result:
            print(f'\n📝 NOTAS ADICIONALES:')
            print(f'   {result["notes"]}')
        
        print('\n✅ Prueba completada exitosamente')
        
        return result
        
    except Exception as e:
        print(f'❌ Error durante la prueba: {str(e)}')
        import traceback
        print(f'🔍 Traceback completo:')
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_marketing_agent())
