#!/usr/bin/env python3
"""
Test script para el Marketing Review Agent
Prueba el agente con datos de ejemplo para verificar su funcionamiento.
"""

import asyncio
import json
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.agents.marketing_review_agent import MarketingReviewAgent
from app.services.ollama_service import get_ollama_service

async def test_marketing_review_agent():
    """
    Prueba el Marketing Review Agent con datos de ejemplo.
    """
    print("🚀 Iniciando prueba del Marketing Review Agent...")
    
    # Verificar que el servicio Ollama esté disponible
    try:
        ollama_service = get_ollama_service()
        print("✅ Servicio Ollama disponible")
    except Exception as e:
        print(f"❌ Error conectando con Ollama: {e}")
        return
    
    # Crear instancia del agente
    agent = MarketingReviewAgent()
    print(f"✅ Agente {agent.agent_name} creado exitosamente")
    
    # Datos de prueba
    test_data = {
        "product_data": {
            "product_name": "Smartwatch Deportivo Pro X1",
            "category": "ELECTRONICS",
            "features": [
                "GPS integrado",
                "Monitor de frecuencia cardíaca",
                "Resistente al agua IP68",
                "Batería de 7 días",
                "Pantalla AMOLED"
            ]
        },
        "previous_results": {
            "ProductDescriptionAgent": {
                "titulo": "Smartwatch Deportivo Pro X1 - Batería de ultra duración de 7 días con GPS activo - Resistencia militar MIL-STD-810G para condiciones extremas - Negro 42mm",
                "descripcion": """Descubre el smartwatch que revolucionará tu estilo de vida activo. El Pro X1 combina tecnología avanzada con diseño robusto para acompañarte en cada aventura.

Con su batería de ultra duración de 7 días, nunca más te preocuparás por quedarte sin energía durante tus entrenamientos más largos. Su GPS de precisión militar te mantendrá siempre en el camino correcto, mientras que el monitor cardíaco profesional cuida de tu salud 24/7.

La resistencia IP68 y certificación MIL-STD-810G garantizan que resista agua, polvo y condiciones extremas. Su pantalla AMOLED de alta definición te brinda información clara incluso bajo el sol intenso.

Ideal para atletas, aventureros y profesionales que buscan rendimiento sin compromisos. Incluye más de 100 modos deportivos, análisis avanzado del sueño y notificaciones inteligentes.

Tu compañero perfecto para superar límites y alcanzar nuevas metas.""",
                "bullet_points": [
                    "⚡ Batería ultra duración: 7 días de uso continuo con GPS activo",
                    "🎯 GPS militar de precisión para navegación exacta en cualquier terreno",
                    "❤️ Monitor cardíaco profesional con alertas de salud en tiempo real",
                    "🛡️ Resistencia extrema: IP68 + MIL-STD-810G para condiciones adversas",
                    "📱 Pantalla AMOLED HD con 100+ modos deportivos y análisis completo"
                ],
                "keywords": [
                    "smartwatch deportivo",
                    "GPS precision",
                    "batería larga duración",
                    "resistente agua",
                    "monitor cardíaco",
                    "fitness tracker",
                    "reloj inteligente",
                    "deportes extremos"
                ],
                "target_price": 299.99
            }
        }
    }
    
    print("\n📋 Datos de prueba preparados:")
    print(f"   Producto: {test_data['product_data']['product_name']}")
    print(f"   Características: {len(test_data['product_data']['features'])} features")
    print(f"   Título actual: {test_data['previous_results']['ProductDescriptionAgent']['titulo'][:60]}...")
    print(f"   Precio objetivo: ${test_data['previous_results']['ProductDescriptionAgent']['target_price']}")
    
    # Ejecutar análisis
    print("\n🔄 Ejecutando análisis de marketing digital...")
    try:
        result = await agent.process(test_data)
        
        if result["success"]:
            print("✅ Análisis completado exitosamente!")
            
            # Mostrar resultados principales
            data = result["data"]
            print(f"\n📊 RESULTADOS DEL ANÁLISIS:")
            print(f"   Puntuación general: {data.get('puntuacion_general', 'N/A')}/10")
            print(f"   Nivel de confianza: {data.get('confidence_score', 0)*100:.1f}%")
            
            # Análisis por categorías
            analisis = data.get("analisis_marketing", {})
            print(f"\n🔍 PUNTUACIONES POR CATEGORÍA:")
            for categoria, datos in analisis.items():
                if isinstance(datos, dict) and 'puntuacion' in datos:
                    print(f"   {categoria.replace('_', ' ').title()}: {datos['puntuacion']}/10")
            
            # Mejoras principales
            mejoras = data.get("mejoras_recomendadas", {})
            print(f"\n💡 MEJORAS PRINCIPALES:")
            
            if 'titulo_optimizado' in mejoras and mejoras['titulo_optimizado'].get('nuevo_titulo'):
                print(f"   📝 Título optimizado:")
                print(f"      {mejoras['titulo_optimizado']['nuevo_titulo'][:80]}...")
            
            if 'prioridades_implementacion' in data and data['prioridades_implementacion']:
                print(f"   🎯 Prioridades:")
                for i, prioridad in enumerate(data['prioridades_implementacion'][:3], 1):
                    print(f"      {i}. {prioridad}")
            
            # Guardar resultado completo
            with open('marketing_review_test_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado completo guardado en: marketing_review_test_result.json")
            
        else:
            print(f"❌ Error en el análisis: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error ejecutando el agente: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Función principal del script de prueba.
    """
    print("=" * 60)
    print("🧪 TEST - Marketing Review Agent")
    print("=" * 60)
    
    # Ejecutar prueba
    asyncio.run(test_marketing_review_agent())
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    print("=" * 60)

if __name__ == "__main__":
    main()
