# archivo: sc/check_models.py

import os
import sys
import django
from django.apps import apps
from django.db import models

# 👉 Agrega el directorio raíz del proyecto al sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

# 👉 Nombre correcto del módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')

# 👉 Inicializa Django
django.setup()

# ✅ Inspecciona los modelos
for model in apps.get_models():
    print(f"\n📦 Modelo: {model.__module__}.{model.__name__}")
    for field in model._meta.get_fields():
        if isinstance(field, models.ForeignKey):
            print(f"🔗 {field.name} (FK → {field.related_model.__name__})")
        else:
            print(f"• {field.name} ({field.__class__.__name__})")




#FUNCIONA PARA VERIFICAR LAS RELACIONES DE LOS MODELOS ANTES DE MIGRACIONES
# archivo: check_models.py
# from django.apps import apps
# from django.db import models

# for model in apps.get_models():
#     print(f"\n📦 Modelo: {model.__module__}.{model.__name__}")
#     for field in model._meta.get_fields():
#         if isinstance(field, models.ForeignKey):
#             print(f"🔗 {field.name} (FK → {field.related_model.__name__})")
#         else:
#             print(f"• {field.name} ({field.__class__.__name__})")
