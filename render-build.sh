#!/usr/bin/env bash
# Script de build para Render - Configuración simplificada compatible con entorno gratuito

set -o errexit  # Detiene el script si hay error

echo "=== Iniciando instalación de dependencias de Python ==="
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo "=== Dependencias de Python instaladas correctamente ==="
