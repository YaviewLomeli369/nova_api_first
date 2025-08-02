import os, django
from django.apps import apps
from django.db.models import NOT_PROVIDED
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')
django.setup()

for app in apps.get_app_configs():
    print(f"\n🧩 App: {app.label}")
    for model in app.get_models():
        print(f"  📦 Modelo: {model.__name__}")
        for f in model._meta.get_fields():
            if f.auto_created and not f.concrete: continue
            tipo = f.get_internal_type()
            extras = []
            if getattr(f, 'primary_key', False): extras.append("PK")
            if getattr(f, 'unique', False): extras.append("unique")
            if getattr(f, 'null', False): extras.append("null")
            if getattr(f, 'blank', False): extras.append("blank")
            if hasattr(f, 'default') and f.default is not NOT_PROVIDED:
                extras.append(f"default={f.default!r}")
            if isinstance(f, (ForeignKey, OneToOneField, ManyToManyField)):
                extras.append(f"rel: {f.related_model.__name__}")
            print(f"    🔹 {f.name} ({tipo}) [{' | '.join(extras)}]" if extras else f"    🔹 {f.name} ({tipo})")
