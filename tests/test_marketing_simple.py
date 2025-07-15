#!/usr/bin/env python3
"""
Test directo del MarketingReviewAgent
"""

import asyncio
import logging
from app.agents.marketing_review_agent import MarketingReviewAgent

logging.basicConfig(level=logging.INFO)

def print_separator(title):
    print("=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_results(result):
    """Función auxiliar para mostrar resultados"""
    if result.get('success'):
        print("✅ STATUS: Ejecutado exitosamente")
        print(f"🎯 CONFIANZA: {result.get('confidence', 'N/A')}")
        print(f"⏱️  TIEMPO: {result.get('processing_time', 'N/A')}s")
        
        if 'data' in result:
            data = result['data']
            print(f"\n📈 DATOS GENERADOS: {type(data).__name__}")
            
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"   🔹 {key}: {type(value).__name__}")
        
        if 'recommendations' in result:
            recs = result['recommendations']
            if isinstance(recs, list):
                print(f"\n💡 RECOMENDACIONES: {len(recs)} encontradas")
                for i, rec in enumerate(recs[:3], 1):
                    print(f"   {i}. {rec}")
    else:
        print("❌ STATUS: Error en ejecución")
        if 'error' in result:
            print(f"🚨 ERROR: {result['error']}")

async def test_marketing_agent():
    print_separator("PRUEBA DEL MARKETING REVIEW AGENT")
    
    try:
        agent = MarketingReviewAgent()
        print(f"✅ MarketingReviewAgent instanciado: {type(agent).__name__}")
        
        # Datos de prueba
        test_data = {
            'product_data': {
                'product_name': 'Termo Acero Inoxidable TechPro',
                'category': 'Home & Kitchen',
                'features': [
                    'Acero inoxidable de grado alimentario',
                    'Aislamiento térmico de doble pared',
                    'Capacidad 500ml'
                ],
                'target_price': 45.0
            },
            'previous_results': {
                'content': {
                    'title': 'TechPro Termo Acero - Aislamiento 24h',
                    'description': 'Termo perfecto para deportistas.',
                    'bullet_points': [
                        'Acero inoxidable resistente',
                        'Mantiene temperatura 24h'
                    ],
                    'keywords': ['termo', 'acero', 'deportistas']
                }
            }
        }
        
        print("\n🔄 Ejecutando MarketingReviewAgent...")
        result = await agent.process(test_data)
        
        print("\n📊 RESULTADOS:")
        print_results(result)
        
        return result
        
    except Exception as e:
        print("\n❌ ERROR DURANTE LA PRUEBA:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_marketing_agent())
    
    if result:
        print("\n✅ Prueba exitosa - Agent disponible y funcional")
    else:
        print("\n❌ Prueba falló - Revisar configuración del agent")
