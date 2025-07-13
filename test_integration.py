import asyncio
import aiohttp
import pytest

@pytest.mark.asyncio
async def test_full_listing_creation_flow():
    """Test completo del flujo de creación de listings"""
    
    base_url = "http://localhost:8000"
    
    # Datos de prueba para un listing completo
    test_data = {
        "product_name": "Smartwatch Deportivo Test Automation",
        "target_customer_description": "Deportistas, atletas, personas activas entre 25-45 años que buscan monitorear su rendimiento y mantener un estilo de vida saludable",
        "category": "Electronics",
        "target_price": 199.99,
        "variants": [],
        "use_situations": [
            "Entrenamiento cardiovascular y running",
            "Natación y deportes acuáticos",
            "Monitoreo de salud diario",
            "Navegación GPS en exteriores",
            "Seguimiento del sueño"
        ],
        "value_proposition": "Smartwatch deportivo con GPS, monitor cardíaco y resistencia al agua. Perfecto para atletas y personas activas que buscan monitorear su rendimiento y salud.",
        "competitive_advantages": [
            "GPS integrado de alta precisión",
            "Monitor de frecuencia cardíaca 24/7", 
            "Resistencia al agua IP68",
            "Batería de 7 días de duración",
            "Pantalla AMOLED de 1.4 pulgadas"
        ],
        "raw_specifications": "Dimensiones: 44mm x 44mm x 12mm, Peso: 45g, Materiales: Aluminio, silicona, cristal zafiro, Colores: Negro, Plata, Azul, Compatibilidad: iOS 14+, Android 8.0+",
        "box_content_description": "1x Smartwatch TechFit, 1x Cargador magnético, 2x Correas de silicona, 1x Manual de usuario, 1x Tarjeta de garantía",
        "warranty_info": "Garantía del fabricante 2 años, cobertura por defectos de fabricación",
        "certifications": ["IP68", "CE", "FCC"],
        "pricing_strategy_notes": "Precio competitivo en el segmento mid-range, posicionado por debajo de Apple Watch pero por encima de marcas económicas",
        "target_keywords": ["smartwatch", "deportivo", "GPS", "monitor cardíaco", "resistente agua", "fitness", "salud", "running"],
        "available_assets": ["product_photos", "lifestyle_photos"],
        "asset_descriptions": ["Fotos del producto en diferentes ángulos", "Fotos de estilo de vida mostrando uso durante ejercicio"]
    }
    
    async with aiohttp.ClientSession() as session:
        # 1. Verificar que el servidor está funcionando
        async with session.get(f"{base_url}/status") as response:
            assert response.status == 200, "El servidor no está respondiendo"
            status_data = await response.json()
            assert status_data["system"] == "online", "El sistema no está online"
            print("✅ Servidor verificado")
        
        # 2. Verificar health check
        async with session.get(f"{base_url}/listings/health") as response:
            assert response.status == 200, "Health check failed"
            health_data = await response.json()
            assert health_data["status"] == "healthy", "Sistema no healthy"
            print("✅ Health check passed")
        
        # 3. Crear un listing completo usando el endpoint simple
        async with session.post(
            f"{base_url}/listings/create-simple",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"Error response: {error_text}")
            assert response.status == 200, f"Error creando listing: {response.status}"
            listing_data = await response.json()
            assert "database_id" in listing_data, "El listing creado debe tener un database_id"
            assert listing_data["database_id"] is not None, "El database_id no debe ser None"
            assert "title" in listing_data, "El listing debe tener un título"
            print(f"✅ Listing creado exitosamente con ID: {listing_data['database_id']}")
        
        # 4. Verificar que el listing se puede recuperar
        listing_id = listing_data["database_id"]
        async with session.get(f"{base_url}/listings/{listing_id}") as response:
            assert response.status == 200, f"Error recuperando listing: {response.status}"
            retrieved_listing = await response.json()
            assert "listing" in retrieved_listing, "La respuesta debe contener un listing"
            listing_info = retrieved_listing["listing"]
            assert listing_info["id"] == listing_id, "El ID del listing recuperado debe coincidir"
            assert listing_info["product_name"] == test_data["product_name"], "El nombre del producto debe coincidir"
            print("✅ Listing recuperado exitosamente")
        
        print("🎉 Test de flujo completo PASADO - Todas las operaciones funcionan correctamente")

@pytest.mark.asyncio
async def test_frontend_endpoints():
    """Test para verificar que los endpoints del frontend son accesibles"""
    
    base_url = "http://localhost:8000"
    
    # Lista de endpoints del frontend que deben ser accesibles
    frontend_endpoints = [
        "/",
        "/styles.css",
        "/app.js",
        "/static/listings.js",
        "/static/dashboard.js",
        "/debug.js"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in frontend_endpoints:
            async with session.get(f"{base_url}{endpoint}") as response:
                # Los archivos HTML/CSS/JS deben ser accesibles (200) o redirigir (30x)
                assert response.status < 400, f"Endpoint {endpoint} no accesible: {response.status}"
                print(f"✅ {endpoint} accesible (status: {response.status})")
    
    print("🎉 Test de endpoints frontend PASADO - Todos los recursos son accesibles")

if __name__ == "__main__":
    # Ejecutar los tests directamente
    asyncio.run(test_full_listing_creation_flow())
    asyncio.run(test_frontend_endpoints())
