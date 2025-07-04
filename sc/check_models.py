# archivo: check_models.py
from django.apps import apps
from django.db import models

for model in apps.get_models():
    print(f"\n📦 Modelo: {model.__module__}.{model.__name__}")
    for field in model._meta.get_fields():
        if isinstance(field, models.ForeignKey):
            print(f"🔗 {field.name} (FK → {field.related_model.__name__})")
        else:
            print(f"• {field.name} ({field.__class__.__name__})")
