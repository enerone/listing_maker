#!/usr/bin/env python3
"""
Script de pruebas para el sistema de creación de listings
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
import pytest

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_database_connection():
    """Prueba la conexión a la base de datos"""
    try:
        from app.database import create_tables, engine
        
        logger.info("🔍 Probando conexión a base de datos...")
        
        # Crear tablas
        await create_tables()
        logger.info("✅ Base de datos conectada y tablas creadas")
        
        # Cerrar conexiones
        await engine.dispose()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_basic_imports():
    """Prueba que todos los imports funcionen"""
    try:
        logger.info("🔍 Probando imports básicos...")
        
        from app.models import ProductInput, ProcessedListing
        from app.agents.product_analysis_agent import ProductAnalysisAgent
        from app.agents.customer_research_agent import CustomerResearchAgent
        from app.agents.value_proposition_agent import ValuePropositionAgent
        from app.agents.listing_orchestrator import ListingOrchestrator
        from app.database import get_db
        from app.services.listing_service import ListingService
        
        logger.info("✅ Todos los imports funcionando")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en imports: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_simple_listing():
    """Prueba creación de listing simple sin Ollama"""
    try:
        logger.info("🔍 Probando creación de listing simple...")
        
        from app.models import ProductInput
        
        # Datos de prueba mínimos
        test_data = {
            "product_name": "Producto Test",
            "category": "Electronics",  # Corregido el valor del enum
            "variants": [],
            "target_customer_description": "Cliente test",
            "use_situations": ["Test"],
            "value_proposition": "Test value",
            "competitive_advantages": ["Test"],
            "raw_specifications": "Test specs",
            "box_content_description": "Test content",
            "warranty_info": "Test warranty",
            "certifications": [],
            "target_price": 99.99,
            "pricing_strategy_notes": "Test",
            "target_keywords": ["test"],
            "available_assets": [],
            "asset_descriptions": []
        }
        
        product_input = ProductInput(**test_data)
        logger.info(f"✅ ProductInput creado: {product_input.product_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en listing simple: {str(e)}")
        return False

async def main():
    """Función principal de pruebas básicas"""
    logger.info("🚀 Iniciando pruebas básicas del sistema")
    logger.info("=" * 50)
    
    tests = [
        ("Imports básicos", test_basic_imports),
        ("Base de datos", test_database_connection),
        ("Listing simple", test_simple_listing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Ejecutando: {test_name}")
        logger.info("-" * 30)
        
        try:
            result = await test_func()
            results[test_name] = result
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"💥 {test_name}: ERROR - {str(e)}")
            results[test_name] = False
    
    # Resumen
    logger.info("\n" + "=" * 50)
    logger.info("📊 RESUMEN")
    logger.info("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        logger.info("🎉 ¡Pruebas básicas completadas! Sistema listo.")
        return True
    else:
        logger.error("⚠️  Algunas pruebas fallaron.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"💥 Error: {str(e)}")
        sys.exit(1)
