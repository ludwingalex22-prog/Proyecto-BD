#!/usr/bin/env bash
# Instala el controlador ODBC para SQL Server antes del build

set -o errexit  # Detiene el script si hay error

echo "=== Instalando dependencias de sistema para SQL Server (ODBC Driver 17) ==="
apt-get update
apt-get install -y curl gnupg apt-transport-https
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
echo "=== Driver ODBC instalado correctamente ==="

echo "=== Instalando dependencias de Python ==="
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo "=== Dependencias Python instaladas correctamente ==="
