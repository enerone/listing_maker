#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api"

async def test_apply_recommendation():
    """
    Prueba el endpoint de aplicar recomendaciones
    """
    async with aiohttp.ClientSession() as session:
        
        # 1. Primero obtener la lista de listings existentes
        logger.info("📋 Obteniendo lista de listings...")
        async with session.get(f"{API_BASE_URL}/listings") as response:
            if response.status == 200:
                listings_data = await response.json()
                listings = listings_data.get("listings", [])
                
                if not listings:
                    logger.error("❌ No hay listings disponibles para probar")
                    return
                
                # Usar el primer listing disponible
                test_listing = listings[0]
                listing_id = test_listing["id"]
                logger.info(f"✅ Usando listing ID: {listing_id} - {test_listing.get('product_name', 'N/A')}")
                
                # 2. Obtener detalles completos del listing
                logger.info(f"📖 Obteniendo detalles del listing {listing_id}...")
                async with session.get(f"{API_BASE_URL}/listings/{listing_id}") as detail_response:
                    if detail_response.status == 200:
                        listing_details = await detail_response.json()
                        
                        # Mostrar estado actual
                        logger.info(f"📝 Estado actual del listing:")
                        logger.info(f"   - Título: {listing_details.get('title', 'N/A')}")
                        logger.info(f"   - Precio: {listing_details.get('target_price', 'N/A')}")
                        logger.info(f"   - Descripción: {len(listing_details.get('description', ''))} caracteres")
                        
                        # 3. Aplicar diferentes tipos de recomendaciones de prueba
                        test_recommendations = [
                            {
                                "agent_name": "seo_visual_agent",
                                "recommendation_text": "Add brand name TechPro to improve discoverability"
                            },
                            {
                                "agent_name": "pricing_strategy_agent", 
                                "recommendation_text": "Adjust price to be more competitive in the market"
                            },
                            {
                                "agent_name": "content_agent",
                                "recommendation_text": "Expand description to include more product benefits"
                            },
                            {
                                "agent_name": "seo_visual_agent",
                                "recommendation_text": "Add keyword optimization for better SEO performance"
                            }
                        ]
                        
                        for i, recommendation in enumerate(test_recommendations, 1):
                            logger.info(f"\n🔧 Aplicando recomendación {i}/4: {recommendation['agent_name']}")
                            logger.info(f"   📝 Texto: {recommendation['recommendation_text']}")
                            
                            async with session.post(
                                f"{API_BASE_URL}/listings/{listing_id}/apply-recommendation",
                                json=recommendation,
                                headers={"Content-Type": "application/json"}
                            ) as apply_response:
                                result = await apply_response.json()
                                
                                if apply_response.status == 200:
                                    logger.info(f"   ✅ Resultado: {result.get('message', 'OK')}")
                                    if result.get('updated_fields'):
                                        logger.info(f"   🔄 Campos actualizados: {list(result['updated_fields'].keys())}")
                                    else:
                                        logger.info(f"   ℹ️  Sin cambios automáticos aplicados")
                                else:
                                    logger.error(f"   ❌ Error {apply_response.status}: {result}")
                        
                        # 4. Verificar estado final
                        logger.info(f"\n📖 Verificando estado final del listing...")
                        async with session.get(f"{API_BASE_URL}/listings/{listing_id}") as final_response:
                            if final_response.status == 200:
                                final_details = await final_response.json()
                                
                                logger.info(f"📝 Estado final del listing:")
                                logger.info(f"   - Título: {final_details.get('title', 'N/A')}")
                                logger.info(f"   - Precio: {final_details.get('target_price', 'N/A')}")
                                logger.info(f"   - Descripción: {len(final_details.get('description', ''))} caracteres")
                                logger.info(f"   - Keywords: {final_details.get('backend_keywords', [])}")
                                logger.info(f"   - Versión: {final_details.get('version', 'N/A')}")
                                
                                # Comparar cambios
                                changes_detected = []
                                if final_details.get('title') != listing_details.get('title'):
                                    changes_detected.append('título')
                                if final_details.get('target_price') != listing_details.get('target_price'):
                                    changes_detected.append('precio')
                                if len(final_details.get('description', '')) != len(listing_details.get('description', '')):
                                    changes_detected.append('descripción')
                                if final_details.get('backend_keywords') != listing_details.get('backend_keywords'):
                                    changes_detected.append('keywords')
                                
                                if changes_detected:
                                    logger.info(f"✅ Cambios detectados en: {', '.join(changes_detected)}")
                                else:
                                    logger.info(f"⚠️  No se detectaron cambios en el listing")
                            else:
                                logger.error(f"❌ Error obteniendo estado final: {final_response.status}")
                    else:
                        logger.error(f"❌ Error obteniendo detalles del listing: {detail_response.status}")
            else:
                logger.error(f"❌ Error obteniendo listings: {response.status}")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas del endpoint apply-recommendation...\n")
    asyncio.run(test_apply_recommendation())
