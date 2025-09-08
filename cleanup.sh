#!/bin/bash

# Script para limpiar archivos innecesarios del proyecto
# Ejecutar: bash cleanup.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[CLEANUP] $1${NC}"; }
warn() { echo -e "${YELLOW}[CLEANUP] WARNING: $1${NC}"; }
error() { echo -e "${RED}[CLEANUP] ERROR: $1${NC}"; }

echo ""
echo "🧹 Limpiando proyecto para despliegue"
echo "===================================="
echo ""

# Eliminar archivos de cache de Python
log "Eliminando cache de Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Eliminar entornos virtuales
log "Eliminando entornos virtuales..."
rm -rf api/env/ 2>/dev/null || true
rm -rf django-web/env/ 2>/dev/null || true
rm -rf env/ 2>/dev/null || true
rm -rf venv/ 2>/dev/null || true

# Eliminar logs antiguos
log "Eliminando logs antiguos..."
rm -rf logs/ 2>/dev/null || true
mkdir -p logs/{api,django,nginx}

# Eliminar archivos temporales
log "Eliminando archivos temporales..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true

# Eliminar staticfiles de Django (se regenerará)
log "Eliminando staticfiles de Django..."
rm -rf django-web/staticfiles/ 2>/dev/null || true

# Eliminar certificados SSL antiguos
log "Eliminando certificados SSL antiguos..."
rm -rf certbot/ 2>/dev/null || true

# Eliminar archivos específicos de Windows
log "Eliminando archivos específicos de Windows..."
find . -name "*.bat" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Eliminar archivos de IDE
log "Eliminando archivos de IDE..."
rm -rf .vscode/ 2>/dev/null || true
rm -rf .idea/ 2>/dev/null || true

# Eliminar archivos de test
log "Eliminando archivos de test..."
find . -name "test_*.py" -delete 2>/dev/null || true
find . -name "*_test.py" -delete 2>/dev/null || true

# Mostrar archivos que quedan
echo ""
log "📁 Estructura final del proyecto:"
tree -I '__pycache__|*.pyc|env|venv|logs|certbot|.git|staticfiles' -L 3 . 2>/dev/null || ls -la

echo ""
log "✅ Limpieza completada"
echo ""
warn "Archivos eliminados:"
echo "  • Cache de Python (__pycache__/, *.pyc)"
echo "  • Entornos virtuales (env/, venv/)"
echo "  • Logs antiguos"
echo "  • Archivos temporales"
echo "  • Staticfiles de Django"
echo "  • Certificados SSL antiguos"
echo "  • Archivos específicos de Windows"
echo "  • Archivos de IDE"
echo "  • Archivos de test"
echo ""
log "📦 El proyecto está listo para despliegue"
