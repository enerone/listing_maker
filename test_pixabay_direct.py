#!/usr/bin/env python3
"""
Script para probar la API de Pixabay directamente y verificar el problema
"""

import asyncio
import aiohttp
import json

async def test_pixabay_api():
    """Prueba directa de la API de Pixabay"""
    
    # API key
    api_key = "9656065-a4094594c34f9ac14c7fc4c39"  # Corregida
    
    # Términos de prueba simples
    test_terms = [
        "smartwatch",
        "watch",
        "apple watch",
        "gaming chair",
        "chair",
        "office chair",
        "water bottle",
        "bottle",
        "stainless steel bottle"
    ]
    
    async with aiohttp.ClientSession() as session:
        for term in test_terms:
            print(f"\nProbando término: '{term}'")
            
            url = "https://pixabay.com/api/"
            params = {
                "key": api_key,
                "q": term,
                "image_type": "photo",
                "per_page": 3,
                "safesearch": "true",
                "order": "popular"
            }
            
            try:
                async with session.get(url, params=params) as response:
                    print(f"Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        hits = data.get("hits", [])
                        print(f"Encontradas: {len(hits)} imágenes")
                        
                        if hits:
                            for i, hit in enumerate(hits[:2]):  # Solo mostrar primeras 2
                                print(f"  {i+1}. {hit.get('tags', '').split(',')[0]}")
                                print(f"     URL: {hit['webformatURL']}")
                                print(f"     Tamaño: {hit['webformatWidth']}x{hit['webformatHeight']}")
                    else:
                        text = await response.text()
                        print(f"Error: {text}")
                        
            except Exception as e:
                print(f"Error en la consulta: {str(e)}")
            
            # Pausa entre consultas
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_pixabay_api())
