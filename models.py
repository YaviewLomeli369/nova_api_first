import os
import django

# Configura la variable de entorno para tu proyecto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')
django.setup()

from django.apps import apps
from django.db.models.fields.related import (
    ForeignKey, OneToOneField, ManyToManyField
)

for app_config in apps.get_app_configs():
    print(f"\n🧩 App: {app_config.label}")
    for model in app_config.get_models():
        print(f"  📦 Modelo: {model.__name__}")
        for field in model._meta.get_fields():
            # Ignorar relaciones inversas generadas automáticamente
            if field.auto_created and not field.concrete:
                continue

            field_info = f"    🔹 Campo: {field.name} ({field.get_internal_type()})"

            # Verifica si es clave primaria
            if getattr(field, 'primary_key', False):
                field_info += " [PRIMARY KEY]"

            # Verifica si es un campo relacional y muestra el modelo relacionado
            if isinstance(field, (ForeignKey, OneToOneField, ManyToManyField)):
                related_model = field.related_model
                field_info += f" [RELACIONA CON: {related_model.__module__}.{related_model.__name__}]"

            print(field_info)