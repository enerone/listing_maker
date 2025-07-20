#!/bin/bash

# Script de limpieza final del sistema
# Este script elimina archivos duplicados y no utilizados de forma segura

echo "🧹 Iniciando limpieza final del sistema..."

cd /home/fabi/code/newlistings

# Crear backup antes de eliminar
echo "📦 Creando backup de agentes a eliminar..."
mkdir -p backups/agents_removed_$(date +%Y%m%d)

# Agentes de imagen duplicados (mantenemos image_search_agent.py que usa el orquestador)
echo "🖼️ Eliminando agentes de imagen duplicados..."
for agent in dynamic_image_search_agent.py improved_image_search_agent.py intelligent_image_search_agent.py relevant_image_search_agent.py real_image_search_agent.py; do
    if [ -f "app/agents/$agent" ]; then
        echo "  - Moviendo $agent a backup..."
        mv "app/agents/$agent" "backups/agents_removed_$(date +%Y%m%d)/"
    fi
done

# Limpiar archivos __pycache__ 
echo "🗑️ Limpiando archivos cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Limpiar archivos .pyc
find . -name "*.pyc" -delete

echo "✅ Limpieza completada!"
echo "📊 Estadísticas:"
echo "   - Agentes de imagen consolidados: 6 → 1"
echo "   - Tests organizados en carpetas temáticas"
echo "   - Archivos cache eliminados"
echo "   - Estructura del proyecto optimizada"

echo ""
echo "📁 Nueva estructura de tests:"
echo "tests/"
echo "├── agents/"
echo "│   ├── description/"
echo "│   ├── image_search/"
echo "│   └── marketing/"
echo "├── api/"
echo "└── integration/"

echo ""
echo "⚠️  NOTA: Los agentes eliminados están en backups/agents_removed_$(date +%Y%m%d)/"
echo "   Si necesitas alguno, puedes restaurarlo desde ahí."
