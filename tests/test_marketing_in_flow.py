#!/usr/bin/env python3
"""
Test para verificar si MarketingReviewAgent se ejecuta en el flujo de creación de listings
"""

import asyncio
import logging
from app.agents.listing_orchestrator import ListingOrchestrator
from app.models import ProductInput, ProductCategory

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_orchestrator_with_marketing_agent():
    print("=" * 60)
    print("🧪 VERIFICANDO MARKETING AGENT EN FLUJO DE CREACIÓN")
    print("=" * 60)
    
    try:
        # Crear instancia del orquestador
        orchestrator = ListingOrchestrator()
        print("✅ ListingOrchestrator instanciado")
        
        # Crear ProductInput de prueba
        product_input = ProductInput(
            product_name="Test Termo MarketingAgent",
            category=ProductCategory.HOME_GARDEN,
            target_customer_description="Deportistas y personas activas",
            use_situations=["Gimnasio", "Oficina", "Viajes"],
            value_proposition="Termo de alta calidad con aislamiento térmico superior",
            competitive_advantages=["Acero inoxidable", "Doble pared", "Diseño ergonómico"],
            raw_specifications="Capacidad: 500ml, Material: Acero inoxidable, Peso: 300g",
            box_content_description="1 termo, 1 manual de usuario",
            warranty_info="Garantía de 2 años",
            target_price=45.0,
            pricing_strategy_notes="Competir con Hydro Flask y Yeti",
            target_keywords=["termo", "acero", "deportistas", "aislamiento"]
        )
        
        print(f"📋 Producto de prueba: {product_input.product_name}")
        print(f"💰 Precio objetivo: ${product_input.target_price}")
        
        print("\n🔄 Ejecutando orquestador completo...")
        
        # Ejecutar la creación del listing
        result = await orchestrator.create_listing(product_input)
        
        print(f"\n📊 RESULTADO DE LA CREACIÓN:")
        print(f"✅ Listing creado: {result.title[:50]}...")
        print(f"🎯 Confidence Score: {result.confidence_score}")
        
        # Obtener las respuestas de los agentes
        print("\n🔍 Verificando respuestas de agentes...")
        agent_responses = await orchestrator.get_last_agent_responses()
        
        if agent_responses:
            print(f"📈 Total de agentes ejecutados: {len(agent_responses)}")
            
            # Buscar específicamente el MarketingReviewAgent
            marketing_found = False
            for agent_name, agent_data in agent_responses.items():
                print(f"   🔹 {agent_name}: {agent_data.status}")
                
                if 'marketing' in agent_name.lower() or agent_name == 'marketing_review':
                    marketing_found = True
                    print(f"   ✅ MARKETING AGENT ENCONTRADO: {agent_name}")
                    
                    # Mostrar datos del marketing agent
                    if agent_data.data:
                        data = agent_data.data
                        print(f"      📊 Datos generados: {type(data).__name__}")
                        if isinstance(data, dict):
                            print(f"      📋 Campos: {list(data.keys())}")
                    
                    if agent_data.recommendations:
                        recs = agent_data.recommendations
                        print(f"      💡 Recomendaciones: {len(recs)}")
                        if recs:
                            print(f"      📝 Primera recomendación: {recs[0][:100]}...")
            
            if not marketing_found:
                print("   ❌ MarketingReviewAgent NO encontrado en las respuestas")
                print(f"   🔍 Agentes disponibles: {list(agent_responses.keys())}")
        else:
            print("❌ No se obtuvieron respuestas de agentes")
        
        # Verificar si las recomendaciones incluyen marketing insights
        if hasattr(result, 'recommendations') and result.recommendations:
            print(f"\n💡 Recomendaciones en el resultado final: {len(result.recommendations)}")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"   {i}. {rec[:100]}...")
        
        return result, agent_responses
        
    except Exception as e:
        print(f"\n❌ ERROR durante la prueba:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    result, agents = asyncio.run(test_orchestrator_with_marketing_agent())
    
    if result:
        print("\n" + "=" * 60)
        print("🏁 RESUMEN DE LA PRUEBA")
        print("=" * 60)
        print("✅ Orquestador ejecutado correctamente")
        print(f"📊 Listing generado con confidence: {result.confidence_score}")
        
        if agents:
            marketing_agents = [name for name in agents.keys() if 'marketing' in name.lower()]
            if marketing_agents:
                print(f"✅ Marketing agents encontrados: {marketing_agents}")
            else:
                print("❌ No se encontraron marketing agents")
        else:
            print("❌ No se pudieron obtener datos de agentes")
    else:
        print("\n❌ La prueba falló - Revisar configuración")
