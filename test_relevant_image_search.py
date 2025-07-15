#!/usr/bin/env python3
"""
Script para probar el agente de imágenes relevantes
"""

import asyncio
import sys
sys.path.append('/home/fabi/code/newlistings')

from app.agents.relevant_image_search_agent import RelevantImageSearchAgent

async def test_relevant_agent():
    """Prueba el agente de imágenes relevantes."""
    
    agent = RelevantImageSearchAgent()
    
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
            "name": "Silla Gaming RGB",
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
        },
        {
            "name": "Silla Oficina Ergonómica",
            "data": {
                "product_data": {
                    "product_name": "Silla Oficina Ergonómica Executive",
                    "category": "Furniture > Office",
                    "features": ["Ergonómica", "Ajustable", "Soporte lumbar", "Giratoria"],
                    "use_cases": ["Oficina", "Trabajo", "Estudios", "Home office"]
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
                
                print(f"Tipo de producto detectado: {data.get('product_type_detected', 'N/A')}")
                
                print("\nTérminos de búsqueda específicos:")
                for i, term in enumerate(data.get("search_terms_used", []), 1):
                    print(f"  {i}. {term}")
                
                print("\nResultados:")
                print(f"  - Imágenes encontradas: {data.get('images_found', 0)}")
                print(f"  - Imágenes procesadas: {data.get('images_downloaded', 0)}")
                print(f"  - Score de confianza: {data.get('confidence_score', 0):.2f}")
                
                # Mostrar imágenes con scores
                images = data.get("downloaded_images", [])
                if images:
                    print(f"\nImágenes específicas del producto:")
                    for i, img in enumerate(images, 1):
                        relevance = img.get('relevance_score', 0)
                        print(f"  {i}. {img.get('title', 'Sin título')}")
                        print(f"     Score: {relevance:.2f} | Término: {img.get('search_term', 'N/A')}")
                        print(f"     URL: {img.get('original_url', 'N/A')}")
                        print(f"     Dimensiones: {img.get('width', 0)}x{img.get('height', 0)}")
                        print()
                
                # Mostrar categorías
                categories = data.get("image_categories", {})
                if categories:
                    print("Categorías de imágenes:")
                    for category, files in categories.items():
                        if files:
                            print(f"  - {category}: {len(files)} imágenes")
                
                # Mostrar recomendaciones
                if result.recommendations:
                    print("\nRecomendaciones específicas:")
                    for rec in result.recommendations:
                        print(f"  - {rec}")
                
                # Mostrar notas
                if result.notes:
                    print("\nNotas del sistema:")
                    for note in result.notes:
                        print(f"  - {note}")
            
            elif result.status == "error":
                print(f"Error: {result.data.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"Error ejecutando prueba: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_relevant_agent())
