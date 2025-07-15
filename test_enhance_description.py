#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de mejora de descripción
"""

import asyncio
import aiohttp
import json

async def test_enhance_description():
    """Prueba la mejora de descripción"""
    
    # URL del endpoint
    url = "http://localhost:8000/api/listings/37/enhance-description"
    
    # Datos de prueba
    test_data = {
        "current_description": "Descubre cómo nuestro alicate para uñas te ayuda a mantener tus uñas perfectas en casa. Perfecto para manicuras rápidas y precisas.",
        "product_info": {
            "product_name": "Alicate para uñas",
            "category": "Health & Personal Care",
            "title": "Alicate para uñas de alta precisión - Cuidado profesional en casa"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Descripción mejorada exitosamente:")
                    print(f"📝 Descripción original ({len(test_data['current_description'])} caracteres):")
                    print(f"   {test_data['current_description']}")
                    print(f"\n📈 Descripción mejorada ({len(result.get('enhanced_description', ''))} caracteres):")
                    print(f"   {result.get('enhanced_description', '')}")
                    print(f"\n📊 Métricas:")
                    print(f"   - Ratio de mejora: {result.get('improvement_metrics', {}).get('improvement_ratio', 0):.2f}x")
                    print(f"   - Caracteres agregados: {result.get('improvement_metrics', {}).get('enhanced_length', 0) - result.get('improvement_metrics', {}).get('original_length', 0)}")
                else:
                    print(f"❌ Error {response.status}: {await response.text()}")
                    
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

if __name__ == "__main__":
    print("🧪 Probando mejora de descripción...")
    asyncio.run(test_enhance_description())
    print("✅ Prueba completada")
