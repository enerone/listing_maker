#!/usr/bin/env python3
"""
Script para probar el ProductDescriptionAgent mejorado
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import ProductInput, ProductCategory
from app.agents.product_description_agent import ProductDescriptionAgent
import json

async def test_improved_description():
    """
    Prueba el agente mejorado para generar descripciones narrativas
    """
    print("🧪 Probando ProductDescriptionAgent mejorado...")
    
    # Crear input de prueba
    product_input = ProductInput(
        product_name="Smartwatch Deportivo Test Automation",
        category=ProductCategory.ELECTRONICS,
        value_proposition="Smartwatch avanzado con funciones deportivas profesionales",
        target_customer_description="Deportistas y entusiastas del fitness que buscan tecnología avanzada",
        use_situations=[
            "Entrenamientos intensivos",
            "Competiciones deportivas",
            "Monitoreo diario de salud",
            "Actividades al aire libre"
        ],
        competitive_advantages=[
            "Batería de larga duración",
            "Resistencia al agua IPX8",
            "GPS de alta precisión",
            "Múltiples sensores deportivos"
        ],
        raw_specifications="Pantalla AMOLED 1.4', batería 7 días, GPS, sensor cardíaco, resistente agua",
        box_content_description="Smartwatch, cargador magnético, manual de usuario, correas adicionales",
        warranty_info="2 años de garantía internacional",
        target_price=199.99
    )
    
    # Crear agente
    agent = ProductDescriptionAgent(temperature=0.7)
    
    # Generar descripción
    print("📝 Generando descripción narrativa...")
    result = await agent.process(product_input)
    
    if result.status == "success":
        print(f"✅ Descripción generada exitosamente!")
        print(f"🎯 Confianza: {result.confidence:.2%}")
        print(f"⏱️ Tiempo: {result.processing_time:.2f}s")
        
        # Mostrar la descripción completa
        full_desc = result.data.get("full_description", "")
        print(f"\n📖 DESCRIPCIÓN COMPLETA ({len(full_desc)} caracteres):")
        print("=" * 80)
        print(full_desc)
        print("=" * 80)
        
        # Verificar que no tenga bullet points
        if "•" in full_desc or "- " in full_desc:
            print("❌ ADVERTENCIA: La descripción contiene bullet points")
        else:
            print("✅ CORRECTO: La descripción es narrativa sin bullet points")
        
        # Mostrar variantes
        variants = result.data.get("description_variants", [])
        if variants:
            print(f"\n📋 VARIANTES DE DESCRIPCIÓN:")
            for i, variant in enumerate(variants, 1):
                print(f"{i}. {variant[:100]}...")
        
        # Guardar resultado completo
        with open('test_description_result.json', 'w', encoding='utf-8') as f:
            json.dump(result.data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultado completo guardado en 'test_description_result.json'")
        
    else:
        print(f"❌ Error: {result.data.get('error', 'Error desconocido')}")
        print(f"📝 Notas: {result.notes}")

if __name__ == "__main__":
    asyncio.run(test_improved_description())
