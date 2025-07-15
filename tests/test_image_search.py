#!/usr/bin/env python3
"""
Script de prueba para el ImageSearchAgent
"""

import asyncio
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.image_search_agent import ImageSearchAgent

async def test_image_search_agent():
    """
    Prueba básica del ImageSearchAgent
    """
    print("🖼️ Probando ImageSearchAgent...")
    
    # Crear instancia del agente
    agent = ImageSearchAgent()
    
    # Datos de prueba
    test_data = {
        "title": "Auriculares Bluetooth Inalámbricos Premium",
        "description": "Auriculares de alta calidad con cancelación de ruido activa, batería de 30 horas y sonido Hi-Fi",
        "category": "Electrónicos > Audio > Auriculares",
        "features": [
            "Cancelación de ruido activa",
            "Batería de 30 horas",
            "Conexión Bluetooth 5.0",
            "Sonido Hi-Fi",
            "Carga rápida",
            "Plegables"
        ],
        "target_audience": "Profesionales y entusiastas de la música",
        "price_range": "$100-200"
    }
    
    print(f"📝 Datos del producto: {test_data['title']}")
    
    try:
        # Ejecutar el agente
        response = await agent.process(test_data)
        
        print(f"✅ Status: {response.status}")
        print(f"📊 Confidence: {response.confidence}")
        print(f"⏱️ Processing time: {response.processing_time}s")
        
        if response.status == "success":
            data = response.data
            
            # Mostrar términos de búsqueda
            search_analysis = data.get("search_analysis", {})
            search_terms = search_analysis.get("search_terms", [])
            
            print(f"\n🔍 Términos de búsqueda generados:")
            for i, term in enumerate(search_terms[:5], 1):
                print(f"  {i}. {term.get('term', 'N/A')} - {term.get('category', 'N/A')} (prioridad: {term.get('priority', 'N/A')})")
            
            # Mostrar estadísticas de imágenes
            print(f"\n📊 Estadísticas de imágenes:")
            print(f"  - Imágenes encontradas: {data.get('found_images', 0)}")
            print(f"  - Imágenes descargadas: {data.get('downloaded_images', 0)}")
            
            image_categories = data.get("image_categories", {})
            print(f"  - Por categorías:")
            for category, count in image_categories.items():
                print(f"    * {category}: {count} imágenes")
            
            # Mostrar recomendaciones
            print(f"\n💡 Recomendaciones ({len(response.recommendations)}):")
            for i, rec in enumerate(response.recommendations[:5], 1):
                print(f"  {i}. {rec}")
            
            # Mostrar imágenes organizadas
            organized_images = data.get("organized_images", {})
            print(f"\n🖼️ Imágenes organizadas:")
            for category, images in organized_images.items():
                if images:
                    print(f"  📁 {category} ({len(images)} imágenes):")
                    for img in images[:2]:  # Mostrar solo las primeras 2
                        print(f"    - {img.get('filename', 'N/A')} (término: {img.get('search_term', 'N/A')})")
        
        else:
            print(f"❌ Error: {data.get('error', 'Error desconocido')}")
        
        print(f"\n📋 Notas adicionales:")
        for note in response.notes:
            print(f"  - {note}")
            
    except Exception as e:
        print(f"❌ Error ejecutando el agente: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_search_agent())
