"""
Test de integración del Marketing Review Agent con el orquestador.
"""

import asyncio
import logging
from app.agents.listing_orchestrator import ListingOrchestrator
from app.models import ProductInput, ProductCategory

# Configurar logging
logging.basicConfig(level=logging.INFO)

async def test_marketing_integration():
    """
    Test básico de integración del marketing review agent.
    """
    print("🧪 Iniciando test de integración del Marketing Review Agent...")
    
    # Datos de prueba simplificados
    product_data = ProductInput(
        product_name="Auriculares Bluetooth Premium XZ-100",
        category=ProductCategory.ELECTRONICS,
        target_customer_description="Profesionales jóvenes que trabajan desde casa y valoran la calidad de audio",
        use_situations=["Trabajo remoto", "Llamadas virtuales", "Música"],
        value_proposition="Auriculares con cancelación de ruido activa y 30 horas de batería para máxima productividad",
        competitive_advantages=["Cancelación de ruido superior", "Batería de larga duración", "Diseño ergonómico"],
        raw_specifications="Bluetooth 5.0, Cancelación activa de ruido, 30h batería, Driver 40mm, Peso 250g",
        box_content_description="Auriculares, cable USB-C, estuche de transporte, manual",
        warranty_info="Garantía de 2 años del fabricante",
        target_price=89.99,
        pricing_strategy_notes="Posicionamiento premium pero accesible",
        target_keywords=["auriculares bluetooth", "cancelacion ruido", "trabajo remoto"]
    )
    
    try:
        # Crear orquestador
        orchestrator = ListingOrchestrator()
        
        # Procesar el listing
        print("📝 Generando listing con marketing review...")
        listing = await orchestrator.create_listing(product_data)
        
        print("✅ Listing generado exitosamente!")
        
        # Verificar que se aplicaron las mejoras de marketing
        print("\n📊 Resultados del Marketing Review:")
        print(f"- Título: {listing.title[:80]}...")
        print(f"- Bullet points: {len(listing.bullet_points)}")
        print(f"- Keywords de búsqueda: {len(listing.search_terms)}")
        print(f"- Backend keywords: {len(listing.seo_keywords.backend_keywords)}")
        
        # Verificar metadata de marketing
        if hasattr(listing, 'metadata') and listing.metadata:
            marketing_metadata = listing.metadata
            if marketing_metadata.get("marketing_review_applied"):
                print("✅ Marketing review aplicado!")
                print(f"- Puntuación general: {marketing_metadata.get('puntuacion_general', 'N/A')}")
                print(f"- Confidence score: {marketing_metadata.get('confidence_score', 'N/A')}")
                print(f"- Prioridades: {len(marketing_metadata.get('prioridades_implementacion', []))}")
            else:
                print("⚠️ Marketing review no se aplicó al metadata")
        else:
            print("⚠️ No se encontró metadata de marketing")
        
        # Verificar respuestas de agentes en el orquestador
        agent_responses = orchestrator._last_agent_responses
        if "marketing_review" in agent_responses:
            marketing_result = agent_responses["marketing_review"]
            print("\n📈 Marketing Review Agent:")
            print(f"- Status: {marketing_result.get('success', 'Unknown')}")
            print(f"- Confidence: {marketing_result.get('confidence', 'N/A')}")
            
            # Mostrar algunos insights del análisis
            analysis_data = marketing_result.get("data", {})
            if "analisis_marketing" in analysis_data:
                analisis = analysis_data["analisis_marketing"]
                print(f"- Persuasión: {analisis.get('persuasion_conversion', {}).get('puntuacion', 'N/A')}/10")
                print(f"- SEO: {analisis.get('seo_visibilidad', {}).get('puntuacion', 'N/A')}/10")
                print(f"- Mobile: {analisis.get('mobile_optimization', {}).get('puntuacion', 'N/A')}/10")
        else:
            print("❌ No se encontró resultado del Marketing Review Agent")
        
        print("\n✅ Test completado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_marketing_integration())
