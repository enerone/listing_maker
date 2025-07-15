"""
Pruebas del agente revisor
"""

import asyncio
import json
from app.agents.review_agent import ReviewAgent


async def test_review_agent():
    """
    Prueba básica del agente revisor
    """
    # Crear instancia del agente
    review_agent = ReviewAgent()
    
    # Datos de prueba
    test_data = {
        "product_data": {
            "product_name": "Smartwatch Pro X1",
            "category": "Electronics",
            "features": ["Waterproof", "GPS", "Heart Rate Monitor", "Long Battery"],
            "use_cases": ["Running", "Swimming", "Daily tracking"],
            "description": "Un smartwatch avanzado para deportistas",
            "target_audience": "Atletas y entusiastas del fitness",
            "price_range": "$200-300",
            "raw_specifications": "Pantalla 1.4 pulgadas, Bluetooth 5.0, 5ATM",
            "target_keywords": ["smartwatch", "fitness", "waterproof", "GPS"]
        },
        "agent_results": {
            "title_agent": {"title": "Smartwatch Pro X1 - Fitness Tracker"},
            "description_agent": {"description": "Smartwatch con GPS y monitor de frecuencia cardíaca"},
            "bullets_agent": {"bullet_points": [
                "GPS integrado",
                "Monitor de frecuencia cardíaca",
                "Resistente al agua",
                "Batería de larga duración"
            ]},
            "keywords_agent": {"keywords": ["smartwatch", "fitness", "GPS", "waterproof"]}
        }
    }
    
    try:
        print("🔍 Iniciando prueba del agente revisor...")
        
        # Ejecutar el agente revisor
        result = await review_agent.process(test_data)
        
        print(f"📊 Estado: {result.status}")
        print(f"🎯 Confianza: {result.confidence:.2f}")
        print(f"⏱️ Tiempo de procesamiento: {result.processing_time:.2f}s")
        print(f"📝 Notas: {result.notes}")
        print(f"💡 Recomendaciones: {len(result.recommendations)} encontradas")
        
        if result.status == "success":
            final_proposal = result.data.get("final_listing", {})
            
            print("\n🎯 PROPUESTA FINAL:")
            print(f"Título optimizado: {final_proposal.get('title', 'N/A')}")
            print(f"Descripción: {final_proposal.get('description', 'N/A')[:100]}...")
            print(f"Bullet points: {len(final_proposal.get('bullet_points', []))}")
            print(f"Keywords: {len(final_proposal.get('keywords', []))}")
            print(f"Categoría sugerida: {final_proposal.get('category', 'N/A')}")
            
            improvements = result.data.get("improvements_summary", {})
            print(f"\n📈 MEJORAS:")
            print(f"Puntuación general: {improvements.get('overall_improvement_score', 0):.1f}/10")
            print(f"Mejoras en título: {improvements.get('title_improvements', [])}")
            print(f"Mejoras en descripción: {improvements.get('description_improvements', [])}")
            
            quality_metrics = result.data.get("quality_metrics", {})
            print(f"\n🏆 MÉTRICAS DE CALIDAD:")
            print(f"Calidad del título: {quality_metrics.get('title_quality', 0):.2f}")
            print(f"Calidad de descripción: {quality_metrics.get('description_quality', 0):.2f}")
            print(f"Calidad de bullets: {quality_metrics.get('bullet_quality', 0):.2f}")
            
            final_recommendations = result.data.get("final_recommendations", [])
            print(f"\n💡 RECOMENDACIONES FINALES:")
            for i, rec in enumerate(final_recommendations[:5], 1):
                print(f"{i}. {rec}")
            
            review_metadata = result.data.get("review_metadata", {})
            print(f"\n📋 METADATOS:")
            print(f"Revisado por: {review_metadata.get('reviewed_by', 'N/A')}")
            print(f"Fecha: {review_metadata.get('review_date', 'N/A')}")
            print(f"Listo para publicar: {review_metadata.get('ready_for_publish', False)}")
            
            # Mostrar estructura completa (opcional)
            print(f"\n🔍 Estructura completa disponible con {len(result.data)} secciones principales")
            
        else:
            print(f"❌ Error: {result.data.get('error', 'Error desconocido')}")
        
        # Limpiar recursos
        await review_agent.cleanup()
        
        print("\n✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        await review_agent.cleanup()


async def test_category_suggestion():
    """
    Prueba específica para sugerencia de categorías
    """
    review_agent = ReviewAgent()
    
    test_products = [
        {
            "product_name": "iPhone 14 Pro",
            "description": "Smartphone with advanced camera",
            "features": ["camera", "5G", "iOS"]
        },
        {
            "product_name": "Nike Running Shoes",
            "description": "Athletic footwear for running",
            "features": ["breathable", "cushioned", "durable"]
        },
        {
            "product_name": "Coffee Maker",
            "description": "Automatic coffee brewing machine",
            "features": ["programmable", "thermal carafe", "easy clean"]
        }
    ]
    
    print("🏷️ Probando sugerencias de categorías...")
    
    for product in test_products:
        category = review_agent._suggest_best_category(
            product["product_name"], 
            product["description"], 
            product["features"]
        )
        match_score = review_agent._calculate_category_match(
            product["product_name"], 
            category
        )
        reasons = review_agent._get_category_reasons(
            product["product_name"], 
            category
        )
        
        print(f"\n📱 Producto: {product['product_name']}")
        print(f"🎯 Categoría sugerida: {category}")
        print(f"📊 Puntuación de coincidencia: {match_score:.2f}")
        print(f"💭 Razones: {reasons}")
    
    await review_agent.cleanup()


async def test_keyword_optimization():
    """
    Prueba específica para optimización de keywords
    """
    review_agent = ReviewAgent()
    
    print("🔍 Probando optimización de keywords...")
    
    optimized_keywords = review_agent._optimize_keywords(
        current_keywords=["smartwatch", "fitness"],
        product_name="Smartwatch Pro X1",
        category="Electronics",
        features=["GPS", "Heart Rate", "Waterproof"]
    )
    
    print(f"🎯 Keywords optimizadas: {optimized_keywords}")
    
    await review_agent.cleanup()


async def run_all_tests():
    """
    Ejecuta todas las pruebas
    """
    print("🧪 INICIANDO PRUEBAS DEL AGENTE REVISOR")
    print("=" * 50)
    
    await test_review_agent()
    
    print("\n" + "=" * 50)
    await test_category_suggestion()
    
    print("\n" + "=" * 50)
    await test_keyword_optimization()
    
    print("\n" + "=" * 50)
    print("🎉 TODAS LAS PRUEBAS COMPLETADAS")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
