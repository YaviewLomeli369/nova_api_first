import os
import django

# Configura la variable de entorno para tu proyecto Django (ajusta el path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')

django.setup()

from django.apps import apps

for app_config in apps.get_app_configs():
    print(f"App: {app_config.label}")
    for model in app_config.get_models():
        print(f"  Modelo: {model.__name__}")
        for field in model._meta.get_fields():
            # Ignorar campos inversos no concretos
            if field.auto_created and not field.concrete:
                continue
            print(f"    Campo: {field.name} ({field.get_internal_type()})")
    print()
