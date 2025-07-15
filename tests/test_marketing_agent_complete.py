#!/usr/bin/env python3
"""
Test completo del MarketingReviewAgent para verificar su funcionamiento
"""

import asyncio
import logging
from app.agents.marketing_review_agent import MarketingReviewAgent

# Configurar logging para ver detalles
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_marketing_agent():
    print("=" * 60)
    print("🧪 PRUEBA COMPLETA DEL MARKETING REVIEW AGENT")
    print("=" * 60)
    
    try:
        # Crear instancia del agente
        agent = MarketingReviewAgent()
        print(f"✅ MarketingReviewAgent instanciado: {type(agent).__name__}")
        
        # Datos de prueba realistas
        test_data = {
            'product_data': {
                'product_name': 'Termo Acero Inoxidable TechPro',
                'category': 'Home & Kitchen',
                'features': [
                    'Acero inoxidable de grado alimentario',
                    'Aislamiento térmico de doble pared',
                    'Diseño ergonómico antideslizante',
                    'Capacidad 500ml',
                    'Libre de BPA'
                ],
                'target_price': 45.0,
                'target_audience': 'Deportistas y personas activas',
                'use_cases': ['Gimnasio', 'Oficina', 'Viajes', 'Deportes']
            },
            'previous_results': {
                'content': {
                    'title': 'TechPro Termo Acero Inoxidable para Deportistas - Aislamiento Térmico 24h | Libre de BPA',
                    'description': 'Termo de acero inoxidable perfecto para deportistas y personas activas. Mantiene las bebidas calientes por 12 horas y frías por 24 horas. Diseño ergonómico con agarre antideslizante.',
                    'bullet_points': [
                        'Acero inoxidable de grado alimentario - Resistente y duradero',
                        'Aislamiento térmico de doble pared - Mantiene temperatura 24h',
                        'Diseño ergonómico antideslizante - Cómodo y seguro',
                        'Capacidad 500ml perfecta para entrenamientos y oficina',
                        'Libre de BPA - Seguro para toda la familia'
                    ],
                    'keywords': ['termo', 'acero inoxidable', 'deportistas', 'aislamiento térmico', 'BPA free']
                },
                'competitive_analysis': {
                    'competitors': ['Hydro Flask', 'Yeti', 'Contigo'],
                    'price_range': [35, 60],
                    'advantages': ['Mejor precio', 'Diseño superior']
                },
                'customer_research': {
                    'pain_points': ['Bebidas que se enfrían rápido', 'Termos pesados'],
                    'desires': ['Larga duración térmica', 'Diseño atractivo']
                }
            }
        }
        
        print("\n📋 Datos de prueba preparados:")
        print(f"   - Producto: {test_data['product_data']['product_name']}")
        print(f"   - Categoría: {test_data['product_data']['category']}")
        print(f"   - Precio objetivo: ${test_data['product_data']['target_price']}")
        print(f"   - Características: {len(test_data['product_data']['features'])} items")
        
        print("\n🔄 Ejecutando MarketingReviewAgent...")
        
        # Ejecutar el agente
        result = await agent.process(test_data)
        
        print("\n📊 RESULTADOS DEL AGENTE:")
        print("=" * 40)
        
        if result.get('success'):
            print("✅ STATUS: Ejecutado exitosamente")
            print(f"🎯 CONFIANZA: {result.get('confidence', 'N/A')}")
            print(f"⏱️  TIEMPO: {result.get('processing_time', 'N/A')}s")
            
            # Analizar datos generados
            if 'data' in result:
                data = result['data']
                print(f"\n📈 DATOS GENERADOS ({type(data).__name__}):")
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"   🔹 {key}: {type(value).__name__}")
                        
                        # Mostrar contenido específico
                        if key == 'conversion_analysis' and isinstance(value, dict):
                            print(f"      - Elementos analizados: {len(value)}")
                            for sub_key in list(value.keys())[:3]:  # Primeros 3
                                print(f"        • {sub_key}: {str(value[sub_key])[:50]}...")
                                
                        elif key == 'marketing_score' and isinstance(value, (int, float)):
                            print(f"      - Score: {value}/100")
                            
                        elif key == 'recommendations' and isinstance(value, list):
                            print(f"      - Total recomendaciones: {len(value)}")
                            for i, rec in enumerate(value[:3], 1):  # Primeras 3
                                print(f"        {i}. {str(rec)[:60]}...")
                                
                        elif key == 'optimization_suggestions':
                            print(f"      - Sugerencias: {len(value) if isinstance(value, list) else 'N/A'}")
                else:
                    print(f"   📄 Contenido: {str(data)[:200]}...")
            
            # Mostrar recomendaciones si existen
            if 'recommendations' in result:
                recs = result['recommendations']
                print(f"\n💡 RECOMENDACIONES DEL AGENTE ({len(recs) if isinstance(recs, list) else 'N/A'}):")
                if isinstance(recs, list):
                    for i, rec in enumerate(recs[:5], 1):  # Primeras 5
                        print(f"   {i}. {rec}")
                else:
                    print(f"   📄 {str(recs)[:200]}...")
            
            # Mostrar notas si existen
            if 'notes' in result:
                notes = result['notes']
                print(f"\n📝 NOTAS: {notes}")
                
        else:
            print("❌ STATUS: Error en ejecución")
            if 'error' in result:
                print(f"🚨 ERROR: {result['error']}")
            if 'details' in result:
                print(f"📋 DETALLES: {result['details']}")
        
        print("\n" + "=" * 60)
        print("🏁 PRUEBA COMPLETADA")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    # Ejecutar la prueba
    result = asyncio.run(test_marketing_agent())
    
    if result:
        print(f"\n✅ Prueba exitosa - Agent disponible y funcional")
    else:
        print(f"\n❌ Prueba falló - Revisar configuración del agent")
