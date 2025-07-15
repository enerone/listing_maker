#!/usr/bin/env python3
"""
Script para probar el endpoint mejorado de búsqueda de imágenes
"""

import asyncio
import json
import requests
import sys
import subprocess
import time
import os

def start_backend():
    """Inicia el backend si no está corriendo"""
    try:
        # Verificar si el backend está corriendo
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✓ Backend ya está corriendo")
            return None
    except:
        print("Iniciando backend...")
        
    # Iniciar el backend
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd="/home/fabi/code/newlistings",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar a que el backend esté listo
    for i in range(30):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ Backend iniciado en {i+1} segundos")
                return process
        except:
            continue
    
    print("✗ Error: No se pudo iniciar el backend")
    return None

def test_image_search_endpoint():
    """Prueba el endpoint de búsqueda de imágenes mejorado"""
    
    # Casos de prueba
    test_cases = [
        {
            "name": "Apple Watch Series 8",
            "data": {
                "product_name": "Apple Watch Series 8",
                "category": "Electronics > Wearables",
                "features": ["GPS", "Fitness tracking", "Heart rate monitor", "Water resistant"],
                "use_cases": ["Fitness", "Health monitoring", "Daily wear", "Sports"],
                "description": "Smartwatch avanzado con GPS y monitoreo de salud",
                "target_audience": "Fitness enthusiasts",
                "price_range": "$300-500"
            }
        },
        {
            "name": "Silla Gaming RGB",
            "data": {
                "product_name": "Silla Gaming Ergonómica RGB",
                "category": "Furniture > Gaming",
                "features": ["Ergonómica", "Reclinable", "Soporte lumbar", "Luces RGB"],
                "use_cases": ["Gaming", "Trabajo", "Oficina", "Streaming"],
                "description": "Silla gaming con iluminación RGB y soporte ergonómico",
                "target_audience": "Gamers",
                "price_range": "$200-400"
            }
        },
        {
            "name": "Termo Acero Inoxidable",
            "data": {
                "product_name": "Termo Acero Inoxidable 500ml",
                "category": "Kitchen > Drinkware",
                "features": ["Acero inoxidable", "Doble pared", "Mantiene temperatura", "Tapa hermética"],
                "use_cases": ["Deportes", "Oficina", "Viajes", "Ejercicio"],
                "description": "Termo de acero inoxidable con aislamiento térmico",
                "target_audience": "Active lifestyle",
                "price_range": "$25-50"
            }
        }
    ]
    
    # Probar cada caso
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"PROBANDO: {test_case['name']}")
        print(f"{'='*60}")
        
        try:
            # Hacer la petición
            response = requests.post(
                "http://localhost:8000/api/listings/search-images",
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print(f"✓ Éxito!")
                    print(f"Tipo de producto detectado: {result.get('product_type', 'N/A')}")
                    print(f"Imágenes encontradas: {result.get('total_images', 0)}")
                    print(f"Confianza: {result.get('confidence', 0):.2f}")
                    print(f"Tiempo de procesamiento: {result.get('processing_time', 0):.2f}s")
                    
                    # Mostrar términos de búsqueda
                    search_terms = result.get("search_terms_used", [])
                    if search_terms:
                        print(f"\nTérminos de búsqueda utilizados:")
                        for i, term in enumerate(search_terms[:5], 1):
                            print(f"  {i}. {term}")
                    
                    # Mostrar primeras imágenes
                    images = result.get("images", [])
                    if images:
                        print(f"\nPrimeras {min(3, len(images))} imágenes:")
                        for i, img in enumerate(images[:3], 1):
                            print(f"  {i}. {img.get('title', 'Sin título')}")
                            print(f"     Score: {img.get('relevance_score', 0):.2f}")
                            print(f"     URL: {img.get('original_url', 'N/A')}")
                            print(f"     Término: {img.get('search_term', 'N/A')}")
                            print()
                    
                    # Mostrar recomendaciones
                    recommendations = result.get("recommendations", [])
                    if recommendations:
                        print(f"Recomendaciones:")
                        for rec in recommendations[:3]:
                            print(f"  - {rec}")
                    
                    # Mostrar notas
                    notes = result.get("notes", [])
                    if notes:
                        print(f"\nNotas:")
                        for note in notes:
                            print(f"  - {note}")
                    
                else:
                    print(f"✗ Error: {result.get('error', 'Error desconocido')}")
                    print(f"Mensaje: {result.get('message', 'N/A')}")
                    
            else:
                print(f"✗ Error HTTP: {response.status_code}")
                print(f"Respuesta: {response.text}")
                
        except Exception as e:
            print(f"✗ Error en la prueba: {str(e)}")
        
        print()

def main():
    """Función principal"""
    print("=== PRUEBA DEL ENDPOINT DE BÚSQUEDA DE IMÁGENES MEJORADO ===")
    
    # Iniciar backend si es necesario
    backend_process = start_backend()
    
    try:
        # Probar el endpoint
        test_image_search_endpoint()
        
    finally:
        # Detener backend si lo iniciamos
        if backend_process:
            print("\nDeteniendo backend...")
            backend_process.terminate()
            backend_process.wait()
            print("✓ Backend detenido")

if __name__ == "__main__":
    main()
