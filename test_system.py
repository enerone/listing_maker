#!/usr/bin/env python3
"""
Script de prueba para el sistema de creación de listings
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.models import ProductInput
from app.agents.listing_orchestrator import ListingOrchestrator

async def test_single_agent():
    """
    Prueba un solo agente para verificar funcionamiento básico
    """
    print("🧪 Probando agente individual...")
    
    # Cargar datos de ejemplo
    with open("example_input.json", "r", encoding="utf-8") as f:
        example_data = json.load(f)
    
    product_input = ProductInput(**example_data)
    
    # Probar el agente de análisis de producto
    from app.agents.product_analysis_agent import ProductAnalysisAgent
    
    agent = ProductAnalysisAgent()
    print(f"Ejecutando {agent.agent_name}...")
    
    start_time = time.time()
    result = await agent.process(product_input.dict())
    end_time = time.time()
    
    print(f"✅ Resultado en {end_time - start_time:.2f}s:")
    print(f"   Status: {result.status}")
    print(f"   Confidence: {result.confidence}")
    print(f"   Datos: {len(result.data)} elementos")
    
    if result.recommendations:
        print(f"   Recomendaciones: {len(result.recommendations)}")
    
    return result.status == "success"

async def test_orchestrator():
    """
    Prueba el orquestador completo
    """
    print("\n🎭 Probando orquestador completo...")
    
    # Cargar datos de ejemplo
    with open("example_input.json", "r", encoding="utf-8") as f:
        example_data = json.load(f)
    
    product_input = ProductInput(**example_data)
    
    orchestrator = ListingOrchestrator()
    print("Ejecutando orquestador...")
    
    start_time = time.time()
    try:
        listing = await orchestrator.create_listing(product_input)
        end_time = time.time()
        
        print(f"✅ Listing generado en {end_time - start_time:.2f}s:")
        print(f"   Título: {listing.title}")
        print(f"   Bullet points: {len(listing.bullet_points)}")
        print(f"   Confidence: {listing.confidence_score}")
        print(f"   Search terms: {len(listing.search_terms)}")
        
        # Mostrar algunas partes del listing
        print(f"\n📝 Bullet Points:")
        for i, bullet in enumerate(listing.bullet_points, 1):
            print(f"   {i}. {bullet}")
        
        print(f"\n🔍 Search Terms: {', '.join(listing.search_terms[:5])}...")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        print(f"❌ Error en {end_time - start_time:.2f}s: {str(e)}")
        return False

async def test_ollama_connection():
    """
    Prueba la conexión con Ollama
    """
    print("🔗 Probando conexión con Ollama...")
    
    try:
        from app.services.ollama_service import get_ollama_service
        
        ollama_service = get_ollama_service()
        
        # Verificar disponibilidad del modelo
        model_available = await ollama_service.check_model_availability()
        print(f"   Modelo {ollama_service.model_name}: {'✅ Disponible' if model_available else '❌ No disponible'}")
        
        if not model_available:
            print("   Intentando descargar modelo...")
            if await ollama_service.pull_model_if_needed():
                print("   ✅ Modelo descargado exitosamente")
            else:
                print("   ❌ Error descargando modelo")
                return False
        
        # Prueba básica de generación
        print("   Probando generación de texto...")
        response = await ollama_service.generate_response(
            prompt="Responde únicamente con 'OK' si puedes leer este mensaje.",
            temperature=0.1
        )
        
        if response["success"]:
            print(f"   ✅ Respuesta: {response['content'][:50]}...")
            return True
        else:
            print(f"   ❌ Error: {response.get('error', 'Desconocido')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

async def main():
    """
    Ejecuta todas las pruebas
    """
    print("🚀 Iniciando pruebas del sistema de listings...\n")
    
    tests = [
        ("Conexión Ollama", test_ollama_connection),
        ("Agente Individual", test_single_agent),
        ("Orquestador Completo", test_orchestrator),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"🧪 Ejecutando: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: ÉXITO\n")
            else:
                print(f"❌ {test_name}: FALLO\n")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}\n")
            results.append((test_name, False))
    
    # Resumen final
    print(f"{'='*50}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Resultado final: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar configuración.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
