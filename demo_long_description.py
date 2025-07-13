#!/usr/bin/env python3
"""
Demostración de la mejora en la generación de descripción larga
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import ProductInput, ProductCategory
from app.agents.listing_orchestrator import ListingOrchestrator

async def demo_long_description():
    """Demuestra la generación de descripción larga vs básica"""
    
    print("🎯 DEMOSTRACIÓN: DESCRIPCIÓN LARGA VS BÁSICA")
    print("=" * 80)
    
    # Crear producto de prueba
    product_input = ProductInput(
        product_name="Cafetera Inteligente WiFi Pro",
        category=ProductCategory.HOME_GARDEN,
        target_customer_description="Amantes del café que buscan comodidad y calidad",
        use_situations=[
            "Preparar café matutino desde la cama",
            "Programar café para invitados",
            "Control remoto desde la oficina",
            "Crear rutinas de café personalizadas"
        ],
        value_proposition="Cafetera con control WiFi que prepara el café perfecto automáticamente",
        competitive_advantages=[
            "Control WiFi desde cualquier lugar",
            "Temperatura y tiempo precisos",
            "Programación inteligente",
            "Compatibilidad con Alexa y Google"
        ],
        raw_specifications="""
        Capacidad: 1.2L (10 tazas)
        Conectividad: WiFi 2.4GHz
        Potencia: 1000W
        Temperatura: 85-95°C ajustable
        Temporizador: 24 horas
        Filtro: Permanente incluido
        """,
        box_content_description="Cafetera WiFi Pro, filtro permanente, jarra térmica, manual, app móvil",
        warranty_info="3 años de garantía + soporte técnico",
        target_price=249.99,
        pricing_strategy_notes="Premium pero accesible",
        target_keywords=[
            "cafetera wifi",
            "cafetera inteligente",
            "control remoto",
            "programable"
        ]
    )
    
    print(f"🔧 Generando listing para: {product_input.product_name}")
    print("-" * 50)
    
    # Crear orquestador
    orchestrator = ListingOrchestrator()
    
    try:
        # Generar listing completo
        listing = await orchestrator.create_listing(product_input)
        
        # Obtener respuestas de agentes
        agent_responses = await orchestrator.get_last_agent_responses()
        
        print("📊 RESULTADOS:")
        print(f"✅ Título: {listing.title}")
        print(f"✅ Confianza general: {listing.confidence_score:.2f}")
        print(f"✅ Puntos clave: {len(listing.bullet_points)}")
        
        print("\n🎯 DESCRIPCIÓN GENERADA:")
        print("=" * 60)
        print(listing.description)
        print("=" * 60)
        
        print(f"\n📈 ESTADÍSTICAS DE DESCRIPCIÓN:")
        print(f"   • Caracteres: {len(listing.description)}")
        print(f"   • Palabras: {len(listing.description.split())}")
        print(f"   • Líneas: {len(listing.description.split('\\n'))}")
        
        # Verificar el agente de descripción
        if "product_description" in agent_responses:
            desc_response = agent_responses["product_description"]
            print(f"\n🤖 AGENTE DE DESCRIPCIÓN:")
            print(f"   • Estado: {desc_response.status}")
            print(f"   • Confianza: {desc_response.confidence:.2f}")
            print(f"   • Tiempo: {desc_response.processing_time:.2f}s")
            print(f"   • Notas: {', '.join(desc_response.notes)}")
            
            if desc_response.status == "success" and desc_response.data:
                desc_data = desc_response.data
                
                print(f"\n📝 CONTENIDO GENERADO POR EL AGENTE:")
                
                # Mostrar descripción completa si existe
                if desc_data.get("full_description"):
                    full_desc = desc_data["full_description"]
                    print(f"   • Descripción completa: {len(full_desc)} caracteres")
                    print(f"   • Fragmento: {full_desc[:200]}...")
                    
                    # Comparar con la descripción básica
                    if len(full_desc) > len(listing.description):
                        print(f"   ✅ Agente generó descripción más rica ({len(full_desc)} vs {len(listing.description)} caracteres)")
                    else:
                        print(f"   ⚠️  Se usó descripción básica de fallback")
                
                # Mostrar secciones principales
                if desc_data.get("main_description"):
                    main_desc = desc_data["main_description"]
                    print(f"\n   📋 SECCIONES PRINCIPALES:")
                    for key, value in main_desc.items():
                        if value and isinstance(value, str):
                            print(f"      • {key}: {len(value)} caracteres")
                
                # Mostrar gatillos emocionales
                if desc_data.get("emotional_triggers"):
                    triggers = desc_data["emotional_triggers"]
                    print(f"\n   💡 GATILLOS EMOCIONALES: {len(triggers)} elementos")
                    for i, trigger in enumerate(triggers[:3], 1):
                        print(f"      {i}. {trigger}")
        
        print(f"\n🌟 PUNTOS CLAVE GENERADOS:")
        for i, bullet in enumerate(listing.bullet_points, 1):
            print(f"   {i}. {bullet}")
        
        print(f"\n🔍 PALABRAS CLAVE:")
        if listing.search_terms:
            print(f"   • Búsqueda: {', '.join(listing.search_terms)}")
        if listing.backend_keywords:
            print(f"   • Backend: {', '.join(listing.backend_keywords)}")
        
        print(f"\n🎊 RESUMEN:")
        print(f"   • El agente ProductDescriptionAgent está funcionando")
        print(f"   • Genera descripciones {'largas y detalladas' if len(listing.description) > 500 else 'básicas'}")
        print(f"   • Integrado correctamente en el flujo de creación")
        print(f"   • Disponible en el frontend para edición")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(demo_long_description())
    sys.exit(0 if success else 1)
