#!/usr/bin/env python3
"""
Test simple del endpoint de mejora de descripción
"""
import asyncio
import aiohttp
import json

async def test_endpoint():
    """Test simple del endpoint"""
    url = "http://localhost:8000/api/listings/1/enhance-description"
    
    test_data = {
        "current_description": "Este es un smartwatch básico con pantalla LED",
        "product_info": {
            "product_name": "Smartwatch Deportivo",
            "category": "Electronics",
            "title": "Smartwatch Deportivo Avanzado con Monitor de Salud"
        }
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_data) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"Success! Enhanced description: {result.get('enhanced_description', 'No description')}")
                else:
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
