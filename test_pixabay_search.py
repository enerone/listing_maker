#!/usr/bin/env python3
"""
Script para probar búsqueda de imágenes usando Pixabay API gratuita.
"""
import requests
import json

def search_images_pixabay(query, per_page=6):
    """
    Busca imágenes en Pixabay usando su API gratuita.
    """
    
    # Pixabay API key gratuita (puedes obtener una en https://pixabay.com/api/docs/)
    # Para demo, usaremos una clave de ejemplo
    api_key = "9656065-a4094594c34f9ac14c7fc4c39"  # Clave de ejemplo
    
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "min_width": 800,
        "per_page": per_page,
        "safesearch": "true"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            images = []
            
            for hit in data.get("hits", []):
                images.append({
                    "url": hit["webformatURL"],
                    "preview_url": hit["previewURL"],
                    "tags": hit["tags"],
                    "user": hit["user"],
                    "views": hit["views"],
                    "downloads": hit["downloads"],
                    "width": hit["webformatWidth"],
                    "height": hit["webformatHeight"],
                    "page_url": hit["pageURL"]
                })
            
            return {
                "success": True,
                "total": data.get("total", 0),
                "images": images
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_image_search():
    """Test básico de búsqueda de imágenes."""
    
    test_queries = [
        "smartwatch",
        "reloj inteligente",
        "gaming chair",
        "silla gamer",
        "office chair",
        "kitchen bottle",
        "termo acero inoxidable"
    ]
    
    print("🔍 Probando búsqueda de imágenes reales con Pixabay")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔎 Buscando: '{query}'")
        
        results = search_images_pixabay(query, per_page=3)
        
        if results["success"]:
            print(f"   ✅ Encontradas: {len(results['images'])} imágenes")
            print(f"   ✅ Total disponibles: {results['total']}")
            
            for i, img in enumerate(results["images"]):
                print(f"   📸 {i+1}. {img['url']}")
                print(f"      Tags: {img['tags'][:50]}...")
                print(f"      Tamaño: {img['width']}x{img['height']}")
                print(f"      Vistas: {img['views']}")
                
        else:
            print(f"   ❌ Error: {results['error']}")
    
    print("\n" + "=" * 60)
    print("✅ Test de búsqueda completado!")

if __name__ == "__main__":
    test_image_search()
