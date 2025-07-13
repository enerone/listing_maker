#!/bin/bash

# Script de inicio para el sistema de creación de listings

echo "🚀 Iniciando Sistema Creador de Listings para AWS"
echo "=================================================="

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ No se encontró el entorno virtual. Creándolo..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Verificar si existe requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ No se encontró requirements.txt"
    exit 1
fi

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Verificar si Ollama está ejecutándose
echo "🔍 Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama no está instalado. Por favor instálalo desde https://ollama.ai"
    echo "   Después ejecuta: ollama pull qwen2.5:latest"
    exit 1
fi

# Verificar si el modelo está disponible
if ! ollama list | grep -q "qwen2.5:latest"; then
    echo "📥 Descargando modelo qwen2.5:latest..."
    ollama pull qwen2.5:latest
else
    echo "✅ Modelo qwen2.5:latest disponible"
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚙️  Creando archivo .env..."
    cp .env.example .env
fi

echo ""
echo "🎉 Sistema listo para usar!"
echo ""
echo "💾 Base de datos SQLite configurada en: listings.db"
echo "🤖 Agentes disponibles:"
echo "   ✅ Product Analysis Agent"
echo "   ✅ Customer Research Agent" 
echo "   ✅ Value Proposition Agent"
echo "   🚧 Technical Specs Agent (próximamente)"
echo "   🚧 Content Agent (próximamente)"
echo "   🚧 Pricing Strategy Agent (próximamente)"
echo "   🚧 SEO & Visual Agent (próximamente)"
echo ""
echo "Comandos disponibles:"
echo "  🧪 Ejecutar pruebas:     python test_basic.py"
echo "  🌐 Iniciar servidor:     uvicorn main:app --reload"
echo "  📖 Ver documentación:    http://localhost:8000/docs"
echo "  🏠 Página principal:     http://localhost:8000"
echo "  📊 Ver estadísticas:     http://localhost:8000/listings/statistics/overview"
echo "  🔍 Ver listings:         http://localhost:8000/listings/"
echo ""
echo "¿Quieres ejecutar las pruebas primero? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🧪 Ejecutando pruebas del sistema..."
    python test_system.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "¿Quieres iniciar el servidor ahora? (y/n)"
        read -r start_server
        
        if [[ "$start_server" =~ ^[Yy]$ ]]; then
            echo "🌐 Iniciando servidor..."
            uvicorn main:app --reload --host 0.0.0.0 --port 8000
        fi
    else
        echo "❌ Las pruebas fallaron. Revisa la configuración antes de iniciar el servidor."
        exit 1
    fi
else
    echo "🌐 Iniciando servidor directamente..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
fi
