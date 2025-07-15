#!/usr/bin/env python3
"""
Script para probar el agente mejorado de búsqueda de imágenes
"""

import asyncio
import sys
sys.path.append('/home/fabi/code/newlistings')

from app.agents.improved_image_search_agent import ImprovedImageSearchAgent

async def test_improved_agent():
    """Prueba el agente mejorado de búsqueda de imágenes."""
    
    agent = ImprovedImageSearchAgent()
    
    # Datos de prueba para diferentes productos
    test_cases = [
        {
            "name": "Apple Watch Series 8",
            "data": {
                "product_data": {
                    "product_name": "Apple Watch Series 8",
                    "category": "Electronics > Wearables",
                    "features": ["GPS", "Fitness tracking", "Heart rate monitor", "Water resistant"],
                    "use_cases": ["Fitness", "Health monitoring", "Daily wear", "Sports"]
                }
            }
        },
        {
            "name": "Silla Gaming Ergonómica",
            "data": {
                "product_data": {
                    "product_name": "Silla Gaming Ergonómica RGB",
                    "category": "Furniture > Gaming",
                    "features": ["Ergonómica", "Reclinable", "Soporte lumbar", "Luces RGB"],
                    "use_cases": ["Gaming", "Trabajo", "Oficina", "Streaming"]
                }
            }
        },
        {
            "name": "Termo Acero Inoxidable",
            "data": {
                "product_data": {
                    "product_name": "Termo Acero Inoxidable 500ml",
                    "category": "Kitchen > Drinkware",
                    "features": ["Acero inoxidable", "Doble pared", "Mantiene temperatura", "Tapa hermética"],
                    "use_cases": ["Deportes", "Oficina", "Viajes", "Ejercicio"]
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"PROBANDO: {test_case['name']}")
        print(f"{'='*60}")
        
        try:
            # Ejecutar búsqueda
            result = await agent.process(test_case["data"])
            
            # Mostrar resultados
            print(f"Status: {result.status}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing time: {result.processing_time:.2f}s")
            
            if result.status == "success" and result.data:
                data = result.data
                
                print(f"\nTérminos de búsqueda específicos:")
                for i, term in enumerate(data.get("search_terms_used", []), 1):
                    print(f"  {i}. {term}")
                
                print(f"\nResultados:")
                print(f"  - Imágenes encontradas: {data.get('images_found', 0)}")
                print(f"  - Imágenes procesadas: {data.get('images_downloaded', 0)}")
                print(f"  - Score de confianza: {data.get('confidence_score', 0):.2f}")
                
                # Mostrar primeras imágenes con scores
                images = data.get("downloaded_images", [])
                if images:
                    print(f"\nPrimeras {min(5, len(images))} imágenes (con scores de relevancia):")
                    for i, img in enumerate(images[:5], 1):
                        relevance = img.get('relevance_score', 0)
                        print(f"  {i}. {img.get('title', 'Sin título')}")
                        print(f"     Score: {relevance:.2f} | Término: {img.get('search_term', 'N/A')}")
                        print(f"     URL: {img.get('original_url', 'N/A')}")
                        print(f"     Dimensiones: {img.get('width', 0)}x{img.get('height', 0)}")
                        print()
                
                # Mostrar categorías
                categories = data.get("image_categories", {})
                if categories:
                    print(f"Categorías de imágenes:")
                    for category, files in categories.items():
                        if files:
                            print(f"  - {category}: {len(files)} imágenes")
                
                # Mostrar recomendaciones
                if result.recommendations:
                    print(f"\nRecomendaciones:")
                    for rec in result.recommendations:
                        print(f"  - {rec}")
                
                # Mostrar notas
                if result.notes:
                    print(f"\nNotas:")
                    for note in result.notes:
                        print(f"  - {note}")
            
            elif result.status == "error":
                print(f"Error: {result.data.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"Error ejecutando prueba: {str(e)}")
            import traceback
            traceback.print_exc()
            
        print()

if __name__ == "__main__":
    asyncio.run(test_improved_agent())
