# =� Amazon Listing Generator with AI Image Generation

Un sistema completo e inteligente para crear listings optimizados de Amazon usando m�ltiples agentes de IA especializados y generaci�n de im�genes con Stable Diffusion.

## ( Caracter�sticas Principales

### > **Sistema Multi-Agente de IA**
- **12 agentes especializados** para diferentes aspectos del listing
- **Generaci�n autom�tica** de t�tulos, descripciones, bullet points y keywords
- **An�lisis competitivo** y optimizaci�n SEO autom�tica
- **Prompts de imagen IA** generados espec�ficamente para cada producto

### <� **Generaci�n de Im�genes con Stable Diffusion**
- **Integraci�n completa** con Stable Diffusion v1.5
- **5 tipos de im�genes** generadas autom�ticamente:
  - =� **Producto Principal** - Fondo limpio, iluminaci�n profesional
  - < **Contextual** - Ambiente natural y realista  
  - <� **Lifestyle** - Personas usando el producto
  - = **Detalle** - Macrofotograf�a de caracter�sticas
  - � **Comparativo** - Comparaci�n con otros productos
- **Optimizado para GPU** (CUDA) para generaci�n r�pida
- **Galer�a integrada** con preview y descarga

### =� **Dashboard Completo**
- **M�tricas en tiempo real** del sistema
- **Gesti�n de listings** con filtros avanzados
- **Interfaz responsive** para desktop y m�vil
- **Visualizaci�n de estad�sticas** y rendimiento

## =� Tecnolog�as Utilizadas

### Backend
- **FastAPI** - Framework web moderno y r�pido
- **SQLite + SQLAlchemy** - Base de datos y ORM
- **Ollama** - Motor de IA local (qwen2.5:latest)
- **Stable Diffusion** - Generaci�n de im�genes
- **PyTorch** - Deep learning framework
- **Diffusers** - Pipeline de modelos de difusi�n

### Frontend
- **HTML5 + JavaScript** puro (sin frameworks pesados)
- **Tailwind CSS** - Estilos modernos y responsive
- **Font Awesome** - Iconograf�a profesional
- **Vue.js patterns** - Reactividad sin framework

### IA y Machine Learning
- **Transformers** - Modelos de lenguaje
- **CUDA Support** - Aceleraci�n por GPU
- **Async Processing** - Procesamiento no bloqueante

## =� Requisitos del Sistema

### Hardware Recomendado
- **GPU NVIDIA** con soporte CUDA (para Stable Diffusion)
- **16GB+ RAM** (8GB m�nimo)
- **20GB+ espacio libre** (para modelos de IA)

### Software
- **Python 3.11+**
- **CUDA 11.8+** (para GPU)
- **Git**
- **Ollama** instalado y configurado

## =� Instalaci�n R�pida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tuusuario/amazon-listing-generator.git
cd amazon-listing-generator
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Ollama
```bash
# Instalar Ollama desde https://ollama.ai
ollama pull qwen2.5:latest
```

### 5. Ejecutar la Aplicaci�n
```bash
python main.py
```

### 6. Abrir en el Navegador
```
http://localhost:8000
```

## =� Gu�a de Uso

### <� **Crear un Nuevo Listing**

1. **Acceder al Generador**
   - Ve a `http://localhost:8000/generator`
   - Completa la informaci�n del producto

2. **Generar Contenido IA**
   - Haz clic en "Generar Listing con IA"
   - Espera a que los agentes procesen la informaci�n
   - Revisa y ajusta el contenido generado

3. **Generar Im�genes IA**
   - Ve a la p�gina de listings: `http://localhost:8000/listings.html`
   - Encuentra tu listing y haz clic en el bot�n morado **"IA"**
   - Espera 1-2 minutos mientras Stable Diffusion genera las im�genes
   - Disfruta de tus 5 im�genes �nicas de producto

### =� **Galer�a de Im�genes**
- **Ver todas las im�genes** generadas en la galer�a
- **Descargar im�genes** individualmente
- **Vista completa** en pantalla completa
- **Gesti�n autom�tica** del almacenamiento

### =� **Dashboard y M�tricas**
- **Monitor del sistema** en tiempo real
- **Estad�sticas de generaci�n** de listings
- **Rendimiento de agentes** de IA
- **Historial completo** de actividad

## =' Configuraci�n Avanzada

### Variables de Entorno
Crea un archivo `.env` en la ra�z del proyecto:

```env
# Base de datos
DATABASE_URL=sqlite+aiosqlite:///./listings.db

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest

# Stable Diffusion
SD_MODEL=runwayml/stable-diffusion-v1-5
SD_DEVICE=cuda  # o 'cpu' si no tienes GPU

# API
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Personalizar Agentes de IA
Los agentes est�n en `/app/agents/` y pueden ser personalizados:

- `listing_orchestrator.py` - Coordinador principal
- `seo_visual_agent.py` - Generaci�n de keywords
- `copywriter_agent.py` - Contenido y descripciones
- `image_generation_service.py` - Generaci�n de im�genes

## =� Estructura del Proyecto

```
amazon-listing-generator/
   app/
      agents/           # Agentes de IA especializados
      api/             # Endpoints de la API
      models/          # Modelos de datos
      services/        # Servicios del sistema
   frontend/            # Interfaz de usuario
      index.html       # Dashboard principal
      listings.html    # Gesti�n de listings
      generator.html   # Generador de listings
      assets/          # CSS, JS, im�genes
   generated_images/    # Im�genes generadas por IA
   requirements.txt     # Dependencias Python
   main.py             # Punto de entrada
   README.md           # Documentaci�n
```

## <� API Endpoints

### Listings
- `GET /listings/` - Listar todos los listings
- `GET /listings/{id}` - Obtener listing espec�fico
- `POST /listings/{id}/generate-ai-images` - Generar im�genes IA
- `DELETE /listings/{id}` - Eliminar listing

### Generaci�n
- `POST /api/generate-listing` - Crear nuevo listing
- `POST /api/keywords/generate` - Generar keywords IA
- `GET /api/suggestions` - Obtener sugerencias

### Im�genes IA
- `GET /listings/ai-images/gallery` - Galer�a de im�genes
- `GET /generated_images/{filename}` - Acceder a imagen

### Sistema
- `GET /status` - Estado del sistema
- `GET /metrics` - M�tricas de rendimiento

## >� Desarrollo y Testing

### Ejecutar Tests
```bash
# Tests unitarios
python -m pytest tests/

# Tests de integraci�n
python -m pytest tests/integration/

# Tests del sistema completo
python test_system.py
```

### Modo Desarrollo
```bash
# Ejecutar con recarga autom�tica
uvicorn main:app --reload --port 8000

# Logs detallados
python main.py --debug
```

## > Contribuir

### 1. Fork del Proyecto
### 2. Crear Feature Branch
```bash
git checkout -b feature/nueva-funcionalidad
```

### 3. Commit Changes
```bash
git commit -m "Agregar nueva funcionalidad incre�ble"
```

### 4. Push y Pull Request
```bash
git push origin feature/nueva-funcionalidad
```

## =� Roadmap

### =� **En Desarrollo**
- [ ] Integraci�n con Amazon SP-API
- [ ] Soporte para m�ltiples idiomas
- [ ] Templates personalizables
- [ ] An�lisis de competencia autom�tico

### =. **Futuras Versiones**
- [ ] Integraci�n con otros marketplaces (eBay, Shopify)
- [ ] Machine Learning para optimizaci�n autom�tica
- [ ] Plugins para Photoshop/GIMP
- [ ] API p�blica para desarrolladores

## = Troubleshooting

### Problema: Stable Diffusion No Funciona
**Soluci�n:**
1. Verificar que CUDA est� instalado: `nvidia-smi`
2. Reinstalar PyTorch con CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`
3. Verificar memoria GPU disponible

### Problema: Ollama No Conecta
**Soluci�n:**
1. Verificar que Ollama est� ejecut�ndose: `ollama list`
2. Descargar el modelo: `ollama pull qwen2.5:latest`
3. Revisar configuraci�n en `.env`

### Problema: Base de Datos Corrupta
**Soluci�n:**
1. Eliminar `listings.db`
2. Ejecutar `python main.py` para recrear
3. Restaurar desde backup si es necesario

## =� Soporte

### = Reportar Bugs
- Crear issue en GitHub con etiqueta `bug`
- Incluir logs, screenshots y pasos para reproducir
- Especificar sistema operativo y versi�n de Python

### =� Solicitar Features
- Crear issue con etiqueta `enhancement`
- Describir el caso de uso y beneficios
- Incluir mockups o ejemplos si es posible

### =� Contacto
- **Email:** soporte@amazon-listing-generator.com
- **Discord:** [Servidor de la Comunidad]
- **Twitter:** [@ListingGenerator]

## =� Licencia

Este proyecto est� bajo la Licencia MIT. Ver `LICENSE` para m�s detalles.

---

## < Agradecimientos

- **Ollama Team** - Por el motor de IA local
- **Stability AI** - Por Stable Diffusion
- **FastAPI Team** - Por el framework web
- **Hugging Face** - Por los modelos pre-entrenados
- **Tailwind CSS** - Por los estilos modernos

---

**Hecho con d por la comunidad de desarrolladores**

=� **�Empieza a crear listings incre�bles hoy mismo!**