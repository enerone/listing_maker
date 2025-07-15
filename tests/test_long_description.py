#!/usr/bin/env python3
"""
Script de prueba para verificar la generación de descripción larga
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import ProductInput, ProductCategory
from app.agents.listing_orchestrator import ListingOrchestrator

async def test_long_description():
    """Prueba la generación de descripción larga"""
    
    # Crear producto de prueba
    product_input = ProductInput(
        product_name="Auriculares Bluetooth Premium XR-500",
        category=ProductCategory.ELECTRONICS,
        target_customer_description="Profesionales que trabajan desde casa y necesitan audio de calidad",
        use_situations=[
            "Reuniones de trabajo virtuales",
            "Escuchar música mientras trabajan",
            "Llamadas importantes",
            "Ejercicio en casa"
        ],
        value_proposition="Auriculares con cancelación de ruido activa y 30 horas de batería",
        competitive_advantages=[
            "Cancelación de ruido líder en el mercado",
            "Batería de larga duración (30 horas)",
            "Conexión Bluetooth 5.2 estable",
            "Diseño ergonómico para uso prolongado"
        ],
        raw_specifications="""
        Conectividad: Bluetooth 5.2
        Batería: 30 horas con ANC activado
        Cancelación de ruido: Híbrida activa
        Respuesta de frecuencia: 20Hz-20kHz
        Peso: 280g
        Carga rápida: 5 min = 2 horas de uso
        """,
        box_content_description="Auriculares XR-500, cable USB-C, cable de audio 3.5mm, estuche de transporte, manual de usuario",
        warranty_info="2 años de garantía internacional",
        target_price=199.99,
        pricing_strategy_notes="Posicionamiento premium competitivo",
        target_keywords=[
            "auriculares bluetooth",
            "cancelación ruido",
            "batería larga duración",
            "trabajo remoto"
        ]
    )
    
    print("🚀 Iniciando prueba de generación de descripción larga...")
    print(f"📦 Producto: {product_input.product_name}")
    
    # Crear orquestador
    orchestrator = ListingOrchestrator()
    
    try:
        # Generar listing completo
        listing = await orchestrator.create_listing(product_input)
        
        print("\n" + "="*80)
        print("📋 LISTING GENERADO")
        print("="*80)
        
        print(f"\n🏷️  TÍTULO:")
        print(listing.title)
        
        print(f"\n📝 DESCRIPCIÓN LARGA:")
        print("-" * 50)
        print(listing.description)
        print("-" * 50)
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   • Longitud descripción: {len(listing.description)} caracteres")
        print(f"   • Palabras: {len(listing.description.split())} palabras")
        print(f"   • Confianza: {listing.confidence_score:.2f}")
        
        print(f"\n🎯 BULLET POINTS:")
        for i, bullet in enumerate(listing.bullet_points, 1):
            print(f"   {i}. {bullet}")
        
        # Verificar si la descripción es larga y detallada
        if len(listing.description) > 500:
            print("\n✅ ÉXITO: Descripción larga generada correctamente")
        else:
            print("\n⚠️  ADVERTENCIA: Descripción parece corta")
        
        # Obtener respuestas de agentes para análisis
        agent_responses = await orchestrator.get_last_agent_responses()
        
        if "product_description" in agent_responses:
            desc_response = agent_responses["product_description"]
            print(f"\n🤖 AGENTE DE DESCRIPCIÓN:")
            print(f"   • Estado: {desc_response.status}")
            print(f"   • Confianza: {desc_response.confidence:.2f}")
            print(f"   • Tiempo: {desc_response.processing_time:.2f}s")
            
            if desc_response.status == "success":
                desc_data = desc_response.data
                
                if desc_data.get("full_description"):
                    print(f"   • Descripción completa: {len(desc_data['full_description'])} caracteres")
                
                if desc_data.get("main_description"):
                    main_desc = desc_data["main_description"]
                    print(f"   • Secciones generadas:")
                    for key, value in main_desc.items():
                        if value and isinstance(value, str):
                            print(f"     - {key}: {len(value)} caracteres")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_long_description())
    sys.exit(0 if success else 1)
