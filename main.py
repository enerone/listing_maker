from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import logging
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api.listings import router as listings_router
from app.api.listing_generator import router as generator_router
from app.api.auth import router as auth_router
from app.database import create_tables
from app.services.ollama_service import get_ollama_service

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear directorios si no existen
IMAGES_DIR = "downloaded_images"
GENERATED_IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

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
        ollama_service = get_ollama_service()
        logger.info(f"Verificando disponibilidad del modelo {ollama_service.model_name}...")
        
        model_available = await ollama_service.check_model_availability()
        if model_available:
            logger.info("✅ Modelo Ollama disponible y listo")
        else:
            logger.warning("⚠️ Modelo Ollama no disponible - funcionalidad limitada")
            
    except Exception as e:
        logger.error(f"Error verificando Ollama: {str(e)}")
        logger.warning("Continuando sin verificación de Ollama...")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")

# Crear la aplicación FastAPI
app = FastAPI(
    title="🚀 Amazon Listing Generator - Sistema Completo",
    description="""
    Sistema completo para crear listings optimizados de Amazon usando múltiples agentes de IA especializados.
    
    ## Características principales:
    - **Dashboard completo** con métricas y estadísticas
    - **Generador de listings** con IA avanzada (/generator)
    - **Gestión de listings** para ver y editar listings guardados
    - **Agentes especializados** para cada aspecto del listing
    - **Optimización SEO** y análisis competitivo automático
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

# Montar directorios de imágenes como archivos estáticos
app.mount("/downloaded_images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/generated_images", StaticFiles(directory=GENERATED_IMAGES_DIR), name="generated_images")

# Montar directorio de imágenes de Stockimg.ai
STOCKIMG_DIR = "stockimg_generated"
os.makedirs(STOCKIMG_DIR, exist_ok=True)
app.mount("/stockimg_generated", StaticFiles(directory=STOCKIMG_DIR), name="stockimg_images")

# Montar archivos estáticos del frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# === RUTAS DE DEBUG Y TESTING ===

@app.get("/test_button_debug.html", response_class=HTMLResponse)
async def test_button_debug():
    """Página de debug para testear botones"""
    if os.path.exists("test_button_debug.html"):
        with open("test_button_debug.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Debug page not found"}

@app.get("/debug_frontend.html", response_class=HTMLResponse)
async def debug_frontend():
    """Página de debug para testear keywords generation"""
    if os.path.exists("debug_frontend.html"):
        with open("debug_frontend.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Debug page not found"}

# === RUTAS PRINCIPALES DEL SISTEMA ===

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página principal - Bienvenida pública o redirige a dashboard si está logueado
    """
    if os.path.exists("frontend/welcome.html"):
        with open("frontend/welcome.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Welcome page not found"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect():
    """
    Dashboard principal - Requiere autenticación (verificada en el frontend)
    """
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            # Inyectar script de verificación de autenticación
            auth_check = """
            <script>
                // Verificar autenticación al cargar el dashboard
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('⚠️ Necesitas iniciar sesión para acceder al dashboard');
                    window.location.href = '/auth';
                }
            </script>
            """
            # Inyectar el script antes del cierre del body
            content = content.replace('</body>', auth_check + '</body>')
            return HTMLResponse(content=content)
    return {"error": "Dashboard not found"}

@app.get("/frontend/index.html", response_class=HTMLResponse)
async def frontend_dashboard():
    """
    Dashboard accesible desde enlaces internos - Requiere autenticación
    """
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            # Inyectar script de verificación de autenticación
            auth_check = """
            <script>
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('⚠️ Necesitas iniciar sesión para acceder al dashboard');
                    window.location.href = '/auth';
                }
            </script>
            """
            content = content.replace('</body>', auth_check + '</body>')
            return HTMLResponse(content=content)
    return {"error": "Dashboard not found"}

@app.get("/frontend/listings.html", response_class=HTMLResponse)
async def frontend_listings():
    """
    Página de listings accesible desde enlaces internos - Requiere autenticación
    """
    if os.path.exists("frontend/listings.html"):
        with open("frontend/listings.html", "r", encoding="utf-8") as f:
            content = f.read()
            # Inyectar script de verificación de autenticación
            auth_check = """
            <script>
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('⚠️ Necesitas iniciar sesión para acceder a los listings');
                    window.location.href = '/auth';
                }
            </script>
            """
            content = content.replace('</body>', auth_check + '</body>')
            return HTMLResponse(content=content)
    return {"error": "Listings page not found"}

# === RUTAS DE ARCHIVOS ESTÁTICOS ===

@app.get("/listings.html", response_class=HTMLResponse)
async def get_listings():
    """Servir página de listings - Requiere autenticación"""
    if os.path.exists("frontend/listings.html"):
        with open("frontend/listings.html", "r", encoding="utf-8") as f:
            content = f.read()
            # Inyectar script de verificación de autenticación
            auth_check = """
            <script>
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('⚠️ Necesitas iniciar sesión para acceder a los listings');
                    window.location.href = '/auth';
                }
            </script>
            """
            content = content.replace('</body>', auth_check + '</body>')
            return HTMLResponse(content=content)
    return {"error": "Listings page not found"}

@app.get("/index.html", response_class=HTMLResponse)
async def get_index():
    """Servir página principal (index.html) - Requiere autenticación"""
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            # Inyectar script de verificación de autenticación
            auth_check = """
            <script>
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('⚠️ Necesitas iniciar sesión para acceder al dashboard');
                    window.location.href = '/auth';
                }
            </script>
            """
            content = content.replace('</body>', auth_check + '</body>')
            return HTMLResponse(content=content)
    return {"error": "Index page not found"}

@app.get("/listing-details.html", response_class=HTMLResponse)
async def get_listing_details():
    """Servir página de detalles de listing"""
    if os.path.exists("frontend/listing-details.html"):
        with open("frontend/listing-details.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Listing details page not found"}

@app.get("/auth", response_class=HTMLResponse)
async def get_auth_page():
    """Servir página de autenticación"""
    if os.path.exists("frontend/auth.html"):
        with open("frontend/auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Auth page not found"}

@app.get("/auth.html", response_class=HTMLResponse)
async def get_auth_html():
    """Servir página de autenticación"""
    if os.path.exists("frontend/auth.html"):
        with open("frontend/auth.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Auth page not found"}

@app.get("/welcome", response_class=HTMLResponse)
async def get_welcome():
    """Servir página de bienvenida"""
    if os.path.exists("frontend/welcome.html"):
        with open("frontend/welcome.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Welcome page not found"}

# === ARCHIVOS JAVASCRIPT Y CSS ===

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

@app.get("/app.js")
async def get_app_js():
    """Servir app.js directamente"""
    if os.path.exists("frontend/app.js"):
        return FileResponse("frontend/app.js", media_type="application/javascript")
    return {"error": "File not found"}

@app.get("/auth.js")
async def get_auth_js():
    """Servir auth.js directamente"""
    if os.path.exists("frontend/auth.js"):
        return FileResponse("frontend/auth.js", media_type="application/javascript")
    return {"error": "File not found"}

@app.get("/styles.css")
async def get_styles_css():
    """Servir styles.css directamente"""
    if os.path.exists("frontend/styles.css"):
        return FileResponse("frontend/styles.css", media_type="text/css")
    return {"error": "File not found"}

# === INCLUIR ROUTERS DE LA API ===

app.include_router(auth_router, prefix="/auth")
app.include_router(listings_router, prefix="/listings")
app.include_router(generator_router)

# === ENDPOINTS DE ESTADO ===

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
