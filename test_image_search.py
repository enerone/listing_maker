#!/usr/bin/env python3

import requests
import json

def test_image_search():
    """Test the image search functionality"""
    
    print("🧪 Testing Image Search Functionality...")
    
    # Test data
    search_data = {
        "product_name": "Smartwatch Pro",
        "description": "Reloj inteligente con GPS y monitor de salud",
        "category": "Electronics",
        "features": ["GPS", "Monitor cardíaco", "Pantalla táctil", "Resistente al agua"],
        "target_audience": "Deportistas y profesionales",
        "price_range": "$150-250"
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/listings/search-images',
            headers={'Content-Type': 'application/json'},
            json=search_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Respuesta exitosa!")
            print(f"📊 Success: {data.get('success', False)}")
            print(f"🖼️  Total imágenes: {data.get('total_images', 0)}")
            print(f"⚡ Tiempo procesamiento: {data.get('processing_time', 'N/A')}")
            print(f"🎯 Confianza: {data.get('confidence', 'N/A')}")
            
            # Show images
            images = data.get('images', [])
            if images:
                print("\n📸 Imágenes encontradas:")
                for i, img in enumerate(images[:5]):  # Show first 5
                    print(f"  {i+1}. {img}")
            
            # Show organized images
            organized = data.get('organized_images', {})
            if organized:
                print("\n📂 Imágenes organizadas por categoría:")
                for category, imgs in organized.items():
                    print(f"  {category}: {len(imgs)} imágenes")
            
            # Show recommendations
            recommendations = data.get('recommendations', [])
            if recommendations:
                print("\n💡 Recomendaciones:")
                for rec in recommendations[:3]:  # Show first 3
                    print(f"  - {rec}")
            
            print("\n🎉 Test completado exitosamente!")
            
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_image_search()
