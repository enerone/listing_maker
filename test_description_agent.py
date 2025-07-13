#!/usr/bin/env python3
"""
Script para probar el nuevo agente de descripción de productos
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.product_description_agent import ProductDescriptionAgent
from app.models import ProductInput

async def test_description_agent():
    """Prueba el agente de descripción de productos"""
    
    # Crear datos de prueba
    product_input = ProductInput(
        product_name="Auriculares Bluetooth Pro X1",
        category="Electronics",
        variants=[],
        target_customer_description="Profesionales y entusiastas de la música entre 25-45 años",
        use_situations=[
            "Trabajar desde casa con llamadas profesionales",
            "Ejercicio y deportes al aire libre",
            "Viajes largos y desplazamientos",
            "Sesiones de estudio y concentración"
        ],
        value_proposition="Auriculares premium con cancelación de ruido activa y 30 horas de batería",
        competitive_advantages=[
            "Cancelación de ruido activa de última generación",
            "Batería de ultra duración (30 horas)",
            "Drivers de alta fidelidad de 40mm",
            "Conexión Bluetooth 5.2 de baja latencia",
            "Diseño ergonómico con materiales premium"
        ],
        raw_specifications="Dimensiones: 19 x 17 x 8 cm, Peso: 280g, Batería: 30 horas, Bluetooth: 5.2, Drivers: 40mm, Impedancia: 32 ohms",
        box_content_description="1x Auriculares Bluetooth Pro X1, 1x Cable USB-C, 1x Cable de audio 3.5mm, 1x Estuche de transporte, 1x Manual de usuario",
        warranty_info="Garantía de 2 años del fabricante con soporte técnico 24/7",
        certifications=[],
        target_price=149.99,
        pricing_strategy_notes="Competir con Sony WH-1000XM4 y Bose QuietComfort",
        target_keywords=["auriculares bluetooth", "cancelación ruido", "batería larga", "alta fidelidad"],
        available_assets=[],
        asset_descriptions=[]
    )
    
    print("🚀 Iniciando prueba del agente de descripción de productos...")
    print(f"📦 Producto: {product_input.product_name}")
    print(f"🎯 Propuesta de valor: {product_input.value_proposition}")
    print("-" * 60)
    
    try:
        # Crear y ejecutar el agente
        agent = ProductDescriptionAgent()
        result = await agent.process(product_input)
        
        print(f"✅ Estado: {result.status}")
        print(f"📊 Confianza: {result.confidence:.2%}")
        print(f"⏱️ Tiempo de procesamiento: {result.processing_time:.2f}s")
        print(f"📝 Notas: {', '.join(result.notes)}")
        print("-" * 60)
        
        if result.status == "success" and result.agent_data:
            data = result.agent_data
            
            # Mostrar la descripción completa
            if data.get("full_description"):
                print("📖 DESCRIPCIÓN COMPLETA:")
                print(data["full_description"])
                print("-" * 60)
            
            # Mostrar secciones principales
            if data.get("main_description"):
                main_desc = data["main_description"]
                
                if main_desc.get("opening_hook"):
                    print("🎪 GANCHO DE APERTURA:")
                    print(main_desc["opening_hook"])
                    print()
                
                if main_desc.get("product_story"):
                    print("📚 HISTORIA DEL PRODUCTO:")
                    print(main_desc["product_story"])
                    print()
                
                if main_desc.get("call_to_action"):
                    print("🚀 LLAMADA A LA ACCIÓN:")
                    print(main_desc["call_to_action"])
                    print()
            
            # Mostrar variantes de descripción
            if data.get("description_variants"):
                print("📝 VARIANTES DE DESCRIPCIÓN:")
                for i, variant in enumerate(data["description_variants"], 1):
                    print(f"  {i}. {variant[:100]}...")
                print()
            
            # Mostrar gatillos emocionales
            if data.get("emotional_triggers"):
                print("💎 GATILLOS EMOCIONALES:")
                for trigger in data["emotional_triggers"]:
                    print(f"  • {trigger}")
                print()
            
            # Mostrar recomendaciones
            if data.get("recommendations"):
                print("💡 RECOMENDACIONES:")
                for rec in data["recommendations"]:
                    print(f"  • {rec}")
        
        else:
            print("❌ Error en el procesamiento:")
            print(f"   {result.agent_data.get('error', 'Error desconocido')}")
    
    except Exception as e:
        print(f"💥 Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_description_agent())
