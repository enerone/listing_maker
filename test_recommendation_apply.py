#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de aplicación de recomendaciones
"""

import asyncio
import aiohttp
import json

async def test_apply_recommendation():
    """Prueba la aplicación de recomendaciones"""
    
    # URL del endpoint
    url = "http://localhost:8000/api/listings/37/apply-recommendation"
    
    # Datos de prueba
    test_data = {
        "agent_name": "ProductAnalysisAgent",
        "recommendation_index": 0,
        "recommendation_text": "Ensure safety compliance is met before listing"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Recomendación aplicada exitosamente:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ Error {response.status}: {await response.text()}")
                    
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

if __name__ == "__main__":
    print("🧪 Probando aplicación de recomendaciones...")
    asyncio.run(test_apply_recommendation())
    print("✅ Prueba completada")
