#!/usr/bin/env python3
"""
Script simple para probar la búsqueda de imágenes de un producto específico
"""

import asyncio
import sys
sys.path.append('/home/fabi/code/newlistings')

from app.agents.image_search_agent import ImageSearchAgent

async def test_simple():
    """Prueba simple de búsqueda de imágenes."""
    
    agent = ImageSearchAgent()
    
    # Datos de prueba para smartwatch
    test_data = {
        "product_data": {
            "product_name": "Apple Watch Series 8",
            "category": "Electronics > Wearables",
            "features": ["GPS", "Fitness tracking", "Heart rate monitor"],
            "use_cases": ["Fitness", "Health monitoring", "Daily wear"]
        }
    }
    
    print("Iniciando búsqueda de imágenes para Apple Watch Series 8...")
    
    try:
        result = await agent.process(test_data)
        
        print(f"Status: {result.status}")
        print(f"Confidence: {result.confidence:.2f}")
        
        if result.status == "success" and result.data:
            data = result.data
            
            print("\nTérminos de búsqueda utilizados:")
            for term in data.get("search_terms_used", []):
                print(f"  - {term}")
            
            print(f"\nImágenes encontradas: {data.get('images_found', 0)}")
            print(f"Imágenes descargadas: {data.get('images_downloaded', 0)}")
            
            # Mostrar URLs de las primeras 3 imágenes
            images = data.get("downloaded_images", [])
            if images:
                print("\nPrimeras 3 imágenes:")
                for i, img in enumerate(images[:3]):
                    print(f"  {i+1}. {img.get('title', 'Sin título')}")
                    print(f"     URL: {img.get('original_url', 'N/A')}")
                    print(f"     Término: {img.get('search_term', 'N/A')}")
                    print()
        
        elif result.status == "error":
            print(f"Error: {result.data.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple())
