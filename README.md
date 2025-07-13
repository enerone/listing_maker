# 🚀 Sistema de Creación de Listings para AWS con Agentes de IA

Este sistema utiliza **FastAPI** y múltiples **agentes de IA especializados** (Ollama con qwen2.5:latest) para crear listings optimizados de productos para Amazon de forma completamente automatizada.

## 🎯 ¿Qué Problemas Resuelve?

El sistema responde automáticamente a las 7 preguntas clave para crear un listing exitoso en Amazon y **los guarda automáticamente en una base de datos** para facilitar su gestión:

1. **🏷️ Producto y Categorización**: ¿Cómo se llama exactamente el producto, en qué categoría de Amazon pensás listarlo y qué variantes ofrece?

2. **👥 Cliente Objetivo**: ¿A qué tipo de cliente va dirigido y en qué situaciones lo usaría?

3. **💎 Propuesta de Valor**: ¿Cuál es su propuesta de valor diferencial frente a la competencia?

4. **🔧 Especificaciones**: ¿Cuáles son las especificaciones esenciales: dimensiones, peso, materiales, compatibilidades?

5. **📦 Contenido y Garantías**: ¿Qué llega en la caja y qué garantía o certificaciones tiene?

6. **💰 Estrategia de Precios**: ¿Cuál es tu estrategia de precio inicial y de promociones?

7. **🔍 SEO y Visuales**: ¿Qué palabras clave querés atacar y con qué activos visuales contás?

## 💾 **Características de Base de Datos**

- **📊 Persistencia Automática**: Todos los listings se guardan automáticamente
- **📈 Versionado**: Historial completo de cambios y versiones
- **🔍 Búsqueda Avanzada**: Filtros por categoría, status, keywords
- **📋 Gestión de Estados**: Draft, Published, Archived
- **🔄 Duplicación**: Clona listings existentes para variantes
- **📊 Estadísticas**: Métricas de performance y usage
- **🔗 Relaciones**: Agrupa productos por proyectos

## 🤖 Agentes de IA Especializados

| Agente | Estado | Descripción |
|--------|---------|-------------|
| **Product Analysis Agent** | ✅ Listo | Analiza productos, categorización y variantes para Amazon |
| **Customer Research Agent** | ✅ Listo | Define target audience, casos de uso y buyer personas |
| **Value Proposition Agent** | ✅ Listo | Identifica propuesta de valor y diferenciación competitiva |
| **Technical Specs Agent** | ✅ Listo | Procesa especificaciones técnicas y requisitos |
| **Content Agent** | ✅ Listo | Gestiona contenido de la caja y garantías |
| **Pricing Strategy Agent** | ✅ Listo | Desarrolla estrategia de precios y promociones |
| **SEO & Visual Agent** | ✅ Listo | Optimiza keywords y gestiona activos visuales |
| **🆕 Marketing Review Agent** | ✅ Listo | Revisa y optimiza el listing desde perspectiva de marketing digital |
| **Listing Orchestrator** | ✅ Listo | Coordina todos los agentes y genera el listing final |

## 📁 Estructura del Proyecto

```text
newlistings/
├── app/
│   ├── agents/              # Agentes de IA especializados
│   │   ├── base_agent.py           # Clase base para agentes
│   │   ├── product_analysis_agent.py
│   │   ├── customer_research_agent.py
│   │   ├── value_proposition_agent.py
│   │   ├── technical_specs_agent.py
│   │   ├── content_agent.py
│   │   ├── pricing_strategy_agent.py
│   │   ├── seo_visual_agent.py
│   │   └── listing_orchestrator.py
│   ├── models/              # Modelos de datos Pydantic y BD
│   │   ├── __init__.py             # ProductInput, ProcessedListing, etc.
│   │   └── database_models.py      # Modelos de base de datos
│   ├── services/            # Servicios de integración
│   │   ├── ollama_service.py       # Servicio de conexión con Ollama
│   │   └── listing_service.py      # Servicio de gestión de BD
│   ├── api/                # Endpoints REST
│   │   └── listings.py             # API de listings
│   ├── utils/              # Utilidades
│   └── database.py         # Configuración de base de datos
├── frontend/               # Interfaz web del usuario
│   ├── index.html                  # Aplicación web principal
│   ├── app.js                      # Lógica del frontend
│   └── styles.css                  # Estilos personalizados
├── venv/                   # Entorno virtual Python
├── listings.db            # Base de datos SQLite
├── requirements.txt        # Dependencias
├── main.py                # Aplicación FastAPI principal
├── example_input.json     # Ejemplo de input para pruebas
├── test_system.py         # Script de pruebas automatizadas
├── start.sh              # Script de inicio automático
└── .env.example          # Variables de entorno de ejemplo
```

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)
```bash
# Clonar y entrar al directorio
cd /home/fabi/code/newlistings

# Ejecutar script de inicio automático
./start.sh
```

### Opción 2: Instalación Manual
```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar y configurar Ollama
# Instalar desde https://ollama.ai
ollama pull qwen2.5:latest

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Ejecutar pruebas (opcional)
python test_system.py

# 6. Iniciar servidor
uvicorn main:app --reload
```

## 🔧 Requisitos Previos

- **Python 3.8+**
- **Ollama** instalado y ejecutándose
- **Modelo qwen2.5:latest** descargado en Ollama
- **8GB RAM mínimo** (recomendado 16GB para mejor rendimiento)

### Instalar Ollama:
```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Iniciar servicio
ollama serve

# Descargar modelo
ollama pull qwen2.5:latest
```

## 🧪 Pruebas del Sistema

```bash
# Ejecutar todas las pruebas
python test_system.py

# Verificar estado del sistema
curl http://localhost:8000/status

# Probar health check
curl http://localhost:8000/listings/health
```

## 🌐 Uso de la API

### 🖥️ **Interfaz Web (Recomendado)**

El sistema incluye una **interfaz web moderna y fácil de usar** que te guía paso a paso:

1. **Accede a la interfaz web**: http://localhost:8000
2. **Sigue el proceso guiado** de 5 pasos:
   - 📝 Información básica del producto
   - 🔧 Especificaciones técnicas
   - 🎯 Mercado target y precios
   - 📋 Revisión final
   - 🎉 Listing generado
3. **Edita y guarda** tu listing directamente desde la web

### Endpoints Principales

#### 🤖 Creación de Listings

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/listings/create` | **Crear listing completo y guardarlo en BD** |
| `POST` | `/listings/analyze-product` | Solo análisis de producto |
| `POST` | `/listings/analyze-customer` | Solo análisis de clientes |
| `POST` | `/listings/analyze-value-proposition` | Solo propuesta de valor |
| `POST` | `/listings/analyze-technical-specs` | **Solo especificaciones técnicas** |
| `POST` | `/listings/analyze-content` | **Solo contenido y garantías** |
| `POST` | `/listings/analyze-pricing-strategy` | **Solo estrategia de precios** |
| `POST` | `/listings/analyze-seo-visual` | **Solo optimización SEO y visual** |

#### 💾 Gestión de Base de Datos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/listings/` | **Listar todos los listings** con filtros |
| `GET` | `/listings/{id}` | **Obtener listing específico** por ID |
| `PUT` | `/listings/{id}` | **Actualizar listing** existente |
| `DELETE` | `/listings/{id}` | **Eliminar listing** |
| `POST` | `/listings/{id}/publish` | **Publicar listing** (cambiar a published) |
| `POST` | `/listings/{id}/duplicate` | **Duplicar listing** para variantes |
| `GET` | `/listings/search/{query}` | **Buscar listings** por texto |
| `GET` | `/listings/statistics/overview` | **Estadísticas** de performance |

#### 🔧 Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Página principal con documentación |
| `GET` | `/docs` | Documentación interactiva Swagger |
| `GET` | `/listings/health` | Estado del sistema y Ollama |

### Ejemplo de Uso

```python
import requests
import json

# Cargar datos de ejemplo
with open('example_input.json', 'r') as f:
    product_data = json.load(f)

# Crear listing completo
response = requests.post(
    'http://localhost:8000/listings/create',
    json=product_data
)

listing = response.json()
print(f"Título generado: {listing['title']}")
print(f"Confidence Score: {listing['confidence_score']}")
```

### Ejemplo con cURL

```bash
# Crear listing completo y guardarlo en BD
curl -X POST "http://localhost:8000/listings/create" \
     -H "Content-Type: application/json" \
     -d @example_input.json

# Listar todos los listings
curl "http://localhost:8000/listings/"

# Buscar listings por categoría
curl "http://localhost:8000/listings/?category=Electronics&status=published"

# Obtener un listing específico
curl "http://localhost:8000/listings/1"

# Duplicar un listing para variante
curl -X POST "http://localhost:8000/listings/1/duplicate"

# Buscar por texto
curl "http://localhost:8000/listings/search/smartwatch"

# Ver estadísticas
curl "http://localhost:8000/listings/statistics/overview"
```

### Gestión de Base de Datos

```python
import requests
import json

# Cargar datos de ejemplo
with open('example_input.json', 'r') as f:
    product_data = json.load(f)

# 1. Crear y guardar listing
response = requests.post(
    'http://localhost:8000/listings/create',
    json=product_data
)
listing = response.json()
listing_id = listing['database_id']
print(f"Listing creado con ID: {listing_id}")

# 2. Obtener todos los listings
listings = requests.get('http://localhost:8000/listings/').json()
print(f"Total listings: {len(listings['listings'])}")

# 3. Buscar listings por filtros
filtered = requests.get(
    'http://localhost:8000/listings/',
    params={'category': 'Electronics', 'status': 'draft'}
).json()

# 4. Publicar listing
publish_response = requests.post(
    f'http://localhost:8000/listings/{listing_id}/publish'
)

# 5. Duplicar para variante
duplicate_response = requests.post(
    f'http://localhost:8000/listings/{listing_id}/duplicate'
)

# 6. Ver estadísticas
stats = requests.get('http://localhost:8000/listings/statistics/overview').json()
print(f"Estadísticas: {stats}")
```

## 📊 Ejemplo de Output

El sistema genera un listing completo con:

```json
{
  "title": "Smartwatch Deportivo Pro X1 - Batería 7 Días GPS - Resistencia Militar - Negro 42mm",
  "bullet_points": [
    "🎯 El único smartwatch que combina seguimiento deportivo profesional con batería de 7 días",
    "✅ Batería de ultra duración de 7 días con GPS activo",
    "💪 Resistencia militar MIL-STD-810G para condiciones extremas",
    "🌟 100+ modos deportivos con métricas avanzadas",
    "🏆 Perfecto para: Durante entrenamientos y ejercicio físico"
  ],
  "search_terms": ["smartwatch deportivo", "reloj inteligente", "fitness tracker"],
  "backend_keywords": ["gps", "resistente", "batería", "deportivo"],
  "confidence_score": 0.89,
  "recommendations": ["Optimizar imágenes lifestyle", "Agregar video demo"]
}
```

## 🔍 Monitoreo y Logs

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Verificar status de Ollama
curl http://localhost:8000/listings/health

# Métricas de rendimiento
curl http://localhost:8000/status
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Ollama no conecta**:
   ```bash
   # Verificar que Ollama esté ejecutándose
   ps aux | grep ollama
   
   # Reiniciar servicio
   ollama serve
   ```

2. **Modelo no disponible**:
   ```bash
   # Listar modelos instalados
   ollama list
   
   # Instalar modelo requerido
   ollama pull qwen2.5:latest
   ```

3. **Errores de dependencias**:
   ```bash
   # Reinstalar dependencias
   pip install --upgrade -r requirements.txt
   ```

4. **Puertos ocupados**:
   ```bash
   # Cambiar puerto en main.py o usar variable de entorno
   export FASTAPI_PORT=8001
   uvicorn main:app --port 8001
   ```

## 🔮 Roadmap

### Próximas Características

- [x] **Agentes Completos**: Technical Specs, Content, Pricing, SEO & Visual ✅
- [ ] **Integración AWS**: Subida automática a Amazon Seller Central
- [ ] **Análisis de Competencia**: Scraping automático de competidores
- [ ] **Optimización A/B**: Testing automático de títulos y descripciones
- [ ] **Métricas de Performance**: Dashboard de conversión y ventas
- [ ] **Multi-idioma**: Soporte para listings en múltiples idiomas
- [ ] **Plantillas Personalizadas**: Templates por categoría de producto

### Mejoras Técnicas

- [ ] **Cache Redis**: Para respuestas de agentes frecuentes
- [ ] **Queue System**: Para procesamiento asíncrono de listings
- [ ] **Rate Limiting**: Control de uso de API
- [ ] **Authentication**: Sistema de usuarios y API keys
- [ ] **Webhooks**: Notificaciones de listings completados

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

- **Documentación**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Issues**: Crear issue en GitHub
- **Email**: Tu email de contacto

---

**¡Hecho con ❤️ para revolucionar la creación de listings en Amazon!**
