from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from contextlib import asynccontextmanager
import os

from app.api.listings import router as listings_router
from app.api.listing_generator import router as generator_router
from app.database import create_tables
from app.services.ollama_service import get_ollama_service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear directorio de imágenes si no existe
IMAGES_DIR = "downloaded_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Startup
    logger.info("Iniciando aplicación de listings...")
    
    # Crear tablas de base de datos
    try:
        logger.info("Creando tablas de base de datos...")
        await create_tables()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {str(e)}")
        raise
    
    # Verificar y configurar Ollama
    try:
        from app.services.ollama_service import get_ollama_service
        
        ollama_service = get_ollama_service()
        logger.info(f"Verificando disponibilidad del modelo {ollama_service.model_name}...")
        
        if not await ollama_service.check_model_availability():
            logger.warning(f"Modelo {ollama_service.model_name} no disponible. Intentando descarga...")
            if await ollama_service.pull_model_if_needed():
                logger.info("Modelo descargado exitosamente")
            else:
                logger.error("Error descargando modelo. Algunas funciones pueden no funcionar.")
        else:
            logger.info("Modelo disponible y listo para usar")
            
    except Exception as e:
        logger.error(f"Error configurando Ollama: {str(e)}")
        logger.warning("La aplicación continuará pero las funciones de IA pueden fallar")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema Creador de Listings para AWS",
    description="""
    Sistema de creación automática de listings para productos de Amazon usando múltiples agentes de IA especializados.
    
    ## Características:
    
    * **Análisis de Producto**: Categorización automática y análisis de variantes
    * **Investigación de Clientes**: Identificación de público objetivo y casos de uso
    * **Propuesta de Valor**: Análisis competitivo y diferenciación
    * **Especificaciones Técnicas**: Procesamiento de especificaciones del producto
    * **Estrategia de Contenido**: Generación de contenido de la caja y garantías
    * **Estrategia de Precios**: Análisis de precios y competencia
    * **SEO y Assets Visuales**: Optimización de keywords y gestión de imágenes
    * **Orquestación**: Coordinación de todos los agentes para generar listings completos
    * **Persistencia**: Almacenamiento y gestión de listings en base de datos
    
    ## Agentes de IA:
    
    El sistema utiliza Ollama con el modelo qwen2.5:latest para potenciar múltiples agentes especializados
    que trabajan en conjunto para crear listings optimizados para Amazon.
    
    ## Base de Datos:
    
    Todos los listings se guardan automáticamente en la base de datos para facilitar:
    - Gestión de versiones
    - Seguimiento de cambios
    - Búsqueda y filtrado
    - Métricas y estadísticas
    - Duplicación y reutilización
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio de imágenes como archivos estáticos
app.mount("/downloaded_images", StaticFiles(directory=IMAGES_DIR), name="images")

# Montar archivos estáticos del frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Servir archivos individuales del frontend directamente ANTES del router
@app.get("/app.js")
async def get_app_js():
    """Servir app.js directamente"""
    if os.path.exists("frontend/app.js"):
        return FileResponse("frontend/app.js", media_type="application/javascript")
    return {"error": "File not found"}

@app.get("/styles.css")
async def get_styles_css():
    """Servir styles.css directamente"""
    if os.path.exists("frontend/styles.css"):
        return FileResponse("frontend/styles.css", media_type="text/css")
    return {"error": "File not found"}

@app.get("/debug.js")
async def get_debug_js():
    """Servir debug.js directamente"""
    if os.path.exists("frontend/debug.js"):
        return FileResponse("frontend/debug.js", media_type="application/javascript")
    return {"error": "File not found"}

@app.get("/listings.js")
async def get_listings_js():
    """Servir listings.js directamente"""
    if os.path.exists("frontend/listings.js"):
        return FileResponse("frontend/listings.js", media_type="application/javascript")
    return {"error": "File not found"}

@app.get("/dashboard.js")
async def get_dashboard_js():
    """Servir dashboard.js directamente"""
    if os.path.exists("frontend/dashboard.js"):
        return FileResponse("frontend/dashboard.js", media_type="application/javascript")
    return {"error": "File not found"}

# Páginas HTML - ANTES de incluir los routers
@app.get("/create-listing.html", response_class=HTMLResponse)
async def get_create_listing():
    """Servir página de creación de listing"""
    if os.path.exists("frontend/create-listing.html"):
        with open("frontend/create-listing.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Create listing page not found"}

@app.get("/dashboard.html", response_class=HTMLResponse)
async def get_dashboard():
    """Servir página del dashboard"""
    if os.path.exists("frontend/dashboard.html"):
        with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Dashboard page not found"}

@app.get("/listings.html", response_class=HTMLResponse)
async def get_listings():
    """Servir página de listings"""
    if os.path.exists("frontend/listings.html"):
        with open("frontend/listings.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Listings page not found"}

@app.get("/debug-dashboard.html", response_class=HTMLResponse)
async def get_debug_dashboard():
    """Servir página de debug dashboard"""
    if os.path.exists("frontend/debug-dashboard.html"):
        with open("frontend/debug-dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Debug dashboard page not found"}

@app.get("/simple-listings.html", response_class=HTMLResponse)
async def get_simple_listings():
    """Servir página de simple listings"""
    if os.path.exists("frontend/simple-listings.html"):
        with open("frontend/simple-listings.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Simple listings page not found"}

@app.get("/monitoring.html", response_class=HTMLResponse)
async def get_monitoring():
    """Servir página de monitoreo del sistema"""
    if os.path.exists("frontend/monitoring.html"):
        with open("frontend/monitoring.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Monitoring page not found"}

@app.get("/test-js.html", response_class=HTMLResponse)
async def get_test_js():
    """Servir página de prueba de JavaScript"""
    if os.path.exists("frontend/test-js.html"):
        with open("frontend/test-js.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Test JS page not found"}

@app.get("/test-links.html", response_class=HTMLResponse)
async def get_test_links():
    """Servir página de prueba de enlaces"""
    if os.path.exists("frontend/test-links.html"):
        with open("frontend/test-links.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Test links page not found"}

@app.get("/index.html", response_class=HTMLResponse)
async def get_index():
    """Servir página principal (index.html)"""
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Index page not found"}

@app.get("/listing-details.html", response_class=HTMLResponse)
async def get_listing_details():
    """Servir página de detalles de listing"""
    if os.path.exists("frontend/listing-details.html"):
        with open("frontend/listing-details.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Listing details page not found"}

# Nueva ruta para la página de prueba del fix del dashboard
@app.get("/test-dashboard-fix.html", response_class=HTMLResponse)
async def get_test_dashboard_fix():
    """Servir página de prueba del fix del dashboard"""
    if os.path.exists("frontend/test-dashboard-fix.html"):
        with open("frontend/test-dashboard-fix.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Test dashboard fix page not found"}

# Incluir routers DESPUÉS de los archivos estáticos y páginas HTML
app.include_router(listings_router, prefix="/listings")
app.include_router(generator_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página principal - Dashboard del sistema
    """
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Dashboard not found"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect():
    """
    Redirige al dashboard principal
    """
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Dashboard not found"}

@app.get("/frontend/index.html", response_class=HTMLResponse)
async def frontend_dashboard():
    """
    Dashboard accesible desde enlaces internos
    """
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Dashboard not found"}

@app.get("/frontend/listings.html", response_class=HTMLResponse)
async def frontend_listings():
    """
    Página de listings accesible desde enlaces internos
    """
    if os.path.exists("frontend/listings.html"):
        with open("frontend/listings.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Listings page not found"}
    
    # Fallback HTML si no existe el frontend
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema Creador de Listings para AWS</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .agent-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .agent-card {
                border-left: 4px solid #667eea;
                padding-left: 15px;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                font-family: monospace;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            .status-ready { background: #d4edda; color: #155724; }
            .status-development { background: #fff3cd; color: #856404; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Sistema Creador de Listings para AWS</h1>
            <p>Múltiples agentes de IA especializados para crear listings optimizados de Amazon</p>
        </div>
        
        <div class="card">
            <h2>🎯 Preguntas que Responde el Sistema</h2>
            <ol>
                <li><strong>Producto y Categorización:</strong> ¿Cómo se llama exactamente el producto, en qué categoría de Amazon pensás listarlo y qué variantes ofrece?</li>
                <li><strong>Cliente Objetivo:</strong> ¿A qué tipo de cliente va dirigido y en qué situaciones lo usaría?</li>
                <li><strong>Propuesta de Valor:</strong> ¿Cuál es su propuesta de valor diferencial frente a la competencia?</li>
                <li><strong>Especificaciones:</strong> ¿Cuáles son las especificaciones esenciales del producto?</li>
                <li><strong>Contenido:</strong> ¿Qué llega en la caja y qué garantía o certificaciones tiene?</li>
                <li><strong>Estrategia de Precios:</strong> ¿Cuál es tu estrategia de precio inicial y de promociones?</li>
                <li><strong>SEO y Visuales:</strong> ¿Qué palabras clave querés atacar y con qué activos visuales contás?</li>
            </ol>
        </div>
        
        <div class="card">
            <h2>🤖 Agentes de IA Especializados</h2>
            <div class="agent-grid">
                <div class="agent-card">
                    <h3>Product Analysis Agent <span class="status-badge status-ready">✅ LISTO</span></h3>
                    <p>Analiza productos, categorización y variantes para Amazon</p>
                </div>
                <div class="agent-card">
                    <h3>Customer Research Agent <span class="status-badge status-ready">✅ LISTO</span></h3>
                    <p>Define target audience, casos de uso y buyer personas</p>
                </div>
                <div class="agent-card">
                    <h3>Value Proposition Agent <span class="status-badge status-ready">✅ LISTO</span></h3>
                    <p>Identifica diferenciadores y ventajas competitivas</p>
                </div>
                <div class="agent-card">
                    <h3>Technical Specs Agent <span class="status-badge status-development">🚧 EN DESARROLLO</span></h3>
                    <p>Procesa especificaciones técnicas y requisitos</p>
                </div>
                <div class="agent-card">
                    <h3>Content Agent <span class="status-badge status-development">🚧 EN DESARROLLO</span></h3>
                    <p>Gestiona contenido de la caja y garantías</p>
                </div>
                <div class="agent-card">
                    <h3>Pricing Strategy Agent <span class="status-badge status-development">🚧 EN DESARROLLO</span></h3>
                    <p>Desarrolla estrategia de precios y promociones</p>
                </div>
                <div class="agent-card">
                    <h3>SEO & Visual Agent <span class="status-badge status-development">🚧 EN DESARROLLO</span></h3>
                    <p>Optimiza keywords y gestiona activos visuales</p>
                </div>
                <div class="agent-card">
                    <h3>Listing Orchestrator <span class="status-badge status-ready">✅ LISTO</span></h3>
                    <p>Coordina todos los agentes y genera el listing final</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🛠️ Endpoints de la API</h2>
            
            <div class="endpoint">
                <strong>POST</strong> /listings/create
                <br><small>Crea un listing completo usando todos los agentes y lo guarda en BD</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /listings/
                <br><small>Lista todos los listings guardados con filtros opcionales</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /listings/{id}
                <br><small>Obtiene detalles completos de un listing específico</small>
            </div>
            
            <div class="endpoint">
                <strong>PUT</strong> /listings/{id}
                <br><small>Actualiza un listing existente (crea nueva versión)</small>
            </div>
            
            <div class="endpoint">
                <strong>DELETE</strong> /listings/{id}
                <br><small>Archiva un listing</small>
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /listings/{id}/publish
                <br><small>Marca un listing como publicado</small>
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /listings/{id}/duplicate
                <br><small>Duplica un listing con un nuevo nombre</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /listings/search/{query}
                <br><small>Búsqueda avanzada de listings</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /listings/statistics/overview
                <br><small>Estadísticas generales del sistema</small>
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /listings/analyze-product
                <br><small>Ejecuta solo el análisis de producto (sin guardar)</small>
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /listings/analyze-customer
                <br><small>Ejecuta solo el análisis de clientes</small>
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /listings/analyze-value-proposition
                <br><small>Ejecuta solo el análisis de propuesta de valor</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /listings/health
                <br><small>Verifica el estado del sistema y conexión con Ollama</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /docs
                <br><small>Documentación interactiva de la API (Swagger UI)</small>
            </div>
        </div>
        
        <div class="card">
            <h2>🚀 Cómo Empezar</h2>
            <ol>
                <li>Asegúrate de que Ollama esté ejecutándose con el modelo qwen2.5:latest</li>
                <li>Visita <a href="/docs">/docs</a> para la documentación interactiva</li>
                <li>Usa el endpoint <a href="/listings/health">/listings/health</a> para verificar el estado</li>
                <li>Comienza creando un listing con <code>POST /listings/create</code></li>
            </ol>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/status")
async def system_status():
    """
    Endpoint rápido de estado del sistema
    """
    try:
        ollama_service = get_ollama_service()
        model_available = await ollama_service.check_model_availability()
        
        return {
            "system": "online",
            "ollama_connected": model_available,
            "model": ollama_service.model_name,
            "agents_ready": 3,  # Product, Customer, Value Proposition
            "agents_total": 7   # Total planificado
        }
    except Exception as e:
        return {
            "system": "online",
            "ollama_connected": False,
            "error": str(e),
            "agents_ready": 0,
            "agents_total": 7
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
