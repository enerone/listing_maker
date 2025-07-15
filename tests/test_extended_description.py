#!/usr/bin/env python3
"""
Script para probar la generación de descripciones extensas y atractivas
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import ProductInput
from app.agents.product_description_agent import ProductDescriptionAgent

async def test_extended_description():
    """
    Prueba la generación de descripción extensa y atractiva
    """
    print("🎯 Iniciando prueba de descripción extensa...")
    
    # Datos de producto de ejemplo (smartwatch)
    product_data = ProductInput(
        product_name="Smartwatch Pro Elite 2024",
        category="Electronics",
        target_price=199.99,
        value_proposition="Smartwatch premium con GPS, monitoreo avanzado de salud, resistencia militar y batería de 14 días",
        target_customer_description="Profesionales activos, deportistas serios y entusiastas de la tecnología que buscan el mejor rendimiento y funcionalidad",
        raw_specifications="Pantalla AMOLED 1.43 pulgadas, GPS dual-band, sensor de oxígeno en sangre, ECG, resistencia al agua 5ATM, batería de 500mAh, procesador de 4 núcleos",
        box_content_description="Smartwatch Pro Elite, base de carga magnética, cable USB-C, correa deportiva adicional, manual de inicio rápido, tarjeta de garantía",
        warranty_info="Garantía internacional de 2 años con servicio técnico 24/7",
        use_situations=[
            "Entrenamiento deportivo profesional",
            "Monitoreo de salud diario",
            "Actividades al aire libre y aventuras",
            "Uso profesional y reuniones de trabajo",
            "Viajes internacionales"
        ],
        competitive_advantages=[
            "Batería de mayor duración del mercado (14 días)",
            "Resistencia militar certificada MIL-STD-810G",
            "GPS dual-band más preciso que la competencia",
            "Monitoreo de salud médico-grade",
            "Ecosistema de apps exclusivo"
        ],
        pricing_strategy_notes="Posicionamiento premium justificado por características superiores",
        target_keywords=[
            "smartwatch premium",
            "GPS preciso",
            "batería larga duración",
            "resistente agua",
            "monitoreo salud"
        ]
    )
    
    # Crear agente mejorado
    agent = ProductDescriptionAgent(temperature=0.7)
    
    # Generar descripción
    print("🔄 Generando descripción extensa...")
    result = await agent.process(product_data)
    
    print(f"📊 Estado: {result.status}")
    print(f"📊 Confianza: {result.confidence:.2%}")
    print(f"⏱️ Tiempo: {result.processing_time:.2f}s")
    print(f"📝 Notas: {', '.join(result.notes)}")
    
    if result.status == "success":
        data = result.data
        
        print("\n" + "="*80)
        print("🎯 DESCRIPCIÓN COMPLETA GENERADA")
        print("="*80)
        
        # Mostrar descripción completa
        if "full_description" in data:
            full_desc = data["full_description"]
            print(f"\n📖 DESCRIPCIÓN COMPLETA ({len(full_desc)} caracteres):")
            print("-" * 60)
            print(full_desc)
            print("-" * 60)
        
        # Mostrar secciones principales
        if "main_description" in data:
            main_desc = data["main_description"]
            print(f"\n🎬 SECCIONES PRINCIPALES:")
            print("-" * 40)
            
            for section_name, section_content in main_desc.items():
                print(f"\n🔹 {section_name.replace('_', ' ').title()}:")
                print(f"   {section_content}")
        
        # Mostrar variantes
        if "description_variants" in data:
            print(f"\n📝 VARIANTES DE DESCRIPCIÓN:")
            print("-" * 40)
            for i, variant in enumerate(data["description_variants"], 1):
                print(f"{i}. {variant}")
        
        # Mostrar gatillos emocionales
        if "emotional_triggers" in data:
            print(f"\n💡 GATILLOS EMOCIONALES:")
            print("-" * 40)
            for i, trigger in enumerate(data["emotional_triggers"], 1):
                print(f"{i}. {trigger}")
        
        # Mostrar palabras poderosas
        if "power_words" in data:
            print(f"\n⚡ PALABRAS PODEROSAS:")
            print("-" * 40)
            for i, word in enumerate(data["power_words"], 1):
                print(f"{i}. {word}")
        
        # Mostrar recomendaciones
        if "recommendations" in data:
            print(f"\n🎯 RECOMENDACIONES:")
            print("-" * 40)
            for i, rec in enumerate(data["recommendations"], 1):
                print(f"{i}. {rec}")
        
        # Estadísticas
        if "full_description" in data:
            full_desc = data["full_description"]
            word_count = len(full_desc.split())
            print(f"\n📊 ESTADÍSTICAS:")
            print(f"   • Caracteres: {len(full_desc)}")
            print(f"   • Palabras: {word_count}")
            print(f"   • Párrafos estimados: {full_desc.count('. ') + 1}")
            
            # Verificar que no tiene bullet points
            has_bullets = any(char in full_desc for char in ['•', '-', '*'])
            print(f"   • Sin bullet points: {'✅' if not has_bullets else '❌'}")
            
            # Verificar longitud mínima
            min_length_ok = len(full_desc) >= 800
            print(f"   • Longitud mínima (800 chars): {'✅' if min_length_ok else '❌'}")
        
        print("\n" + "="*80)
        print("✅ PRUEBA COMPLETADA")
        print("="*80)
        
        # Guardar resultado en archivo
        with open("extended_description_test.json", "w", encoding="utf-8") as f:
            json.dump({
                "status": result.status,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "notes": result.notes,
                "data": data
            }, f, indent=2, ensure_ascii=False)
        
        print("💾 Resultado guardado en 'extended_description_test.json'")
    
    else:
        print(f"\n❌ Error: {result.data}")

if __name__ == "__main__":
    asyncio.run(test_extended_description())
