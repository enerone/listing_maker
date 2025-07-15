#!/usr/bin/env python3
"""
Script de prueba rápida después de la limpieza
"""
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_imports():
    """Test que los módulos principales se importan correctamente"""
    try:
        from app.api.listings import router
        from app.services.recommendation_service import RecommendationService
        from app.services.listing_service import ListingService
        from app.models import ProductInput, ProcessedListing
        
        logger.info("✅ Todos los imports principales funcionan")
        return True
    except Exception as e:
        logger.error(f"❌ Error en imports: {e}")
        return False

async def test_basic_functionality():
    """Test básico de funcionalidad"""
    try:
        from app.services.recommendation_service import RecommendationService
        from app.models import ProductInput
        
        # Test RecommendationService
        rec_service = RecommendationService()
        logger.info("✅ RecommendationService se inicializa correctamente")
        
        # Test ProductInput
        product_input = ProductInput(
            product_name="Test Product",
            category="Electronics",
            target_customer_description="Tech enthusiasts",
            use_situations=["Gaming"],
            value_proposition="High performance",
            competitive_advantages=["Fast", "Reliable"],
            raw_specifications="Test specs",
            box_content_description="Product, Manual",
            warranty_info="1 year",
            target_price=99.99,
            pricing_strategy_notes="Competitive",
            target_keywords=["tech", "gaming"]
        )
        logger.info("✅ ProductInput se crea correctamente")
        logger.info(f"✅ Product name: {product_input.product_name}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error en funcionalidad básica: {e}")
        return False

async def main():
    """Función principal de test"""
    logger.info("🧪 Iniciando tests post-limpieza...")
    
    # Test imports
    imports_ok = await test_imports()
    
    # Test funcionalidad básica
    basic_ok = await test_basic_functionality()
    
    if imports_ok and basic_ok:
        logger.info("🎉 ¡Todos los tests pasaron! El sistema está listo para usar.")
        return 0
    else:
        logger.error("💥 Algunos tests fallaron. Revisar errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
