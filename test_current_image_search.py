#!/usr/bin/env python3
"""
Script para probar el sistema actual de búsqueda de imágenes
y ver qué tipo de imágenes está devolviendo.
"""

import asyncio
import sys
sys.path.append('/home/fabi/code/newlistings')

from app.agents.image_search_agent import ImageSearchAgent

async def test_current_image_search():
    """Prueba el sistema actual de búsqueda de imágenes."""
    
    # Crear agente
    agent = ImageSearchAgent()
    
    # Datos de prueba para diferentes tipos de productos
    test_cases = [
        {
            "name": "Smartwatch Apple Watch",
            "data": {
                "product_data": {
                    "product_name": "Apple Watch Series 8",
                    "category": "Electronics > Wearables",
                    "features": ["GPS", "Fitness tracking", "Heart rate monitor"],
                    "use_cases": ["Fitness", "Health monitoring", "Daily wear"]
                }
            }
        },
        {
            "name": "Silla Gaming",
            "data": {
                "product_data": {
                    "product_name": "Silla Gaming Ergonómica",
                    "category": "Furniture > Gaming",
                    "features": ["Ergonómica", "Reclinable", "Soporte lumbar"],
                    "use_cases": ["Gaming", "Trabajo", "Oficina"]
                }
            }
        },
        {
            "name": "Termo Acero Inoxidable",
            "data": {
                "product_data": {
                    "product_name": "Termo Acero Inoxidable 500ml",
                    "category": "Kitchen > Drinkware",
                    "features": ["Acero inoxidable", "Doble pared", "Mantiene temperatura"],
                    "use_cases": ["Deportes", "Oficina", "Viajes"]
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"PROBANDO: {test_case['name']}")
        print(f"{'='*50}")
        
        try:
            # Ejecutar búsqueda
            result = await agent.process(test_case["data"])
            
            # Mostrar resultados
            print(f"Status: {result.status}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing time: {result.processing_time:.2f}s")
            
            if result.status == "success" and result.data:
                data = result.data
                print(f"\nTérminos de búsqueda utilizados:")
                for term in data.get("search_terms_used", []):
                    print(f"  - {term}")
                
                print(f"\nImágenes encontradas: {data.get('images_found', 0)}")
                print(f"Imágenes descargadas: {data.get('images_downloaded', 0)}")
                
                # Mostrar detalles de imágenes
                images = data.get("downloaded_images", [])
                if images:
                    print(f"\nDetalles de imágenes:")
                    for i, img in enumerate(images[:3]):  # Solo mostrar primeras 3
                        print(f"  {i+1}. {img.get('title', 'Sin título')}")
                        print(f"     URL: {img.get('original_url', 'N/A')}")
                        print(f"     Término: {img.get('search_term', 'N/A')}")
                        print(f"     Dimensiones: {img.get('width', 0)}x{img.get('height', 0)}")
                        print()
                
                # Mostrar recomendaciones
                if result.recommendations:
                    print(f"Recomendaciones:")
                    for rec in result.recommendations:
                        print(f"  - {rec}")
            
            elif result.status == "error":
                print(f"Error: {result.data.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"Error ejecutando prueba: {str(e)}")
            
        print()

if __name__ == "__main__":
    asyncio.run(test_current_image_search())
