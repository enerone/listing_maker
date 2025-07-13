"""
Test de endpoint completo con Marketing Review Agent integrado.
"""

import asyncio
import requests
import json

def test_api_integration():
    """
    Test del endpoint API completo con marketing review.
    """
    print("🧪 Testing API endpoint with Marketing Review Agent...")
    
    # Datos de prueba para el endpoint
    test_data = {
        "product_name": "Smartwatch Fitness Pro 2024",
        "category": "Electronics",
        "target_customer_description": "Deportistas y profesionales activos que buscan monitorear su salud",
        "use_situations": ["Ejercicio", "Trabajo", "Vida diaria"],
        "value_proposition": "Smartwatch con monitoreo avanzado de salud y 14 días de batería",
        "competitive_advantages": ["Batería de larga duración", "Sensores precisos", "App intuitiva"],
        "raw_specifications": "Pantalla AMOLED 1.4', GPS, monitor de frecuencia cardíaca, resistente al agua IP68",
        "box_content_description": "Smartwatch, cargador magnético, correas adicionales, manual",
        "warranty_info": "Garantía de 1 año del fabricante",
        "target_price": 199.99,
        "pricing_strategy_notes": "Posicionamiento medio-premium",
        "target_keywords": ["smartwatch", "fitness tracker", "monitor cardiaco", "GPS"]
    }
    
    try:
        print("📡 Enviando petición al endpoint...")
        
        # Intentar conectar al endpoint local
        response = requests.post(
            "http://localhost:8000/api/listings/create",
            json=test_data,
            timeout=300  # 5 minutos máximo
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Listing creado exitosamente!")
            
            # Verificar campos de marketing
            listing = result.get("listing", {})
            print(f"\n📊 Resultados del API:")
            print(f"- ID del listing: {listing.get('database_id', 'N/A')}")
            print(f"- Título: {listing.get('title', 'N/A')[:60]}...")
            print(f"- Bullet points: {len(listing.get('bullet_points', []))}")
            print(f"- Keywords: {len(listing.get('search_terms', []))}")
            
            # Verificar metadata de marketing
            metadata = listing.get("metadata", {})
            if metadata.get("marketing_review_applied"):
                print(f"\n✅ Marketing Review aplicado!")
                print(f"- Puntuación: {metadata.get('puntuacion_general', 'N/A')}")
                print(f"- Confidence: {metadata.get('confidence_score', 'N/A')}")
                print(f"- Prioridades: {len(metadata.get('prioridades_implementacion', []))}")
            else:
                print("⚠️ Marketing review no detectado en metadata")
            
            return True
            
        else:
            print(f"❌ Error en API: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ No se pudo conectar al servidor API")
        print("ℹ️ Asegúrate de que el servidor esté ejecutándose con: python main.py")
        return False
        
    except Exception as e:
        print(f"❌ Error en test de API: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_integration()
