#!/bin/bash

set -e  # Detiene la ejecución si algún comando falla

echo "Eliminando base de datos..."
rm -f db.sqlite3

echo "Eliminando archivos de migración..."
find . -path "*/migrations/*.py" ! -name "__init__.py" -delete

echo "Desinstalando Django..."
pip uninstall -y django

echo "Instalando Django..."
pip install django

echo "Creando nuevas migraciones..."
python manage.py makemigrations

echo "Aplicando migraciones..."
python manage.py migrate

echo "Ejecutando script final..."
python new.py
