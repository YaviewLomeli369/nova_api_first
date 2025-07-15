import os
import django
from django.apps import apps
from django.db import models

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')  # Ajusta al nombre de tu archivo de settings
django.setup()

# Función para obtener detalles de los modelos y campos

app_label = 'core'  # Reemplaza con el nombre de tu app (por ejemplo, 'core')
app = apps.get_app_config(app_label)

# Recorremos todos los modelos definidos en la app
for model in app.get_models():
    print(f"Modelo: {model.__name__}")

    # Recorremos todos los campos del modelo
    for field in model._meta.get_fields():
        field_name = field.name
        field_type = field.get_internal_type()
        related_model = getattr(field, 'related_model', None)
        related_name = getattr(field, 'related_name', None)

        if related_model:
            print(f"  Campo: {field_name} (Tipo: {field_type}) - Relacionado con: {related_model.__name__} (related_name: {related_name})")
        else:
            print(f"  Campo: {field_name} (Tipo: {field_type})")

    print("\n" + "="*40 + "\n")

# Ejecutar la función para obtener la información


# from django.apps import apps
# from django.db import models

# def get_model_info():
#     model_info = {}

#     # Iteramos sobre todos los modelos de la app
#     for model in apps.get_models():
#         model_name = model._meta.model_name
#         model_fields = []

#         # Iteramos sobre todos los campos de cada modelo
#         for field in model._meta.fields:
#             field_info = {
#                 'name': field.name,
#                 'type': str(field.get_internal_type()),  # Tipo de campo
#                 'null': field.null,  # Si puede ser null
#                 'blank': field.blank,  # Si puede estar vacío
#                 'default': field.default,  # Valor por defecto
#             }

#             # Si el campo es una relación (ForeignKey, ManyToManyField, OneToOneField)
#             if isinstance(field, models.ForeignKey):
#                 field_info['relationship'] = {
#                     'type': 'ForeignKey',
#                     'related_model': field.related_model._meta.model_name,
#                 }
#             elif isinstance(field, models.ManyToManyField):
#                 field_info['relationship'] = {
#                     'type': 'ManyToMany',
#                     'related_model': field.related_model._meta.model_name,
#                 }
#             elif isinstance(field, models.OneToOneField):
#                 field_info['relationship'] = {
#                     'type': 'OneToOne',
#                     'related_model': field.related_model._meta.model_name,
#                 }

#             model_fields.append(field_info)

#         model_info[model_name] = model_fields

#     return model_info

# def print_model_info():
#     model_info = get_model_info()

#     for model_name, fields in model_info.items():
#         print(f"Modelo: {model_name}")
#         for field in fields:
#             print(f"  Campo: {field['name']}")
#             print(f"    Tipo: {field['type']}")
#             print(f"    Permite null: {field['null']}")
#             print(f"    Permite vacío: {field['blank']}")
#             print(f"    Valor por defecto: {field['default']}")

#             if 'relationship' in field:
#                 print(f"    Relación: {field['relationship']['type']} con el modelo '{field['relationship']['related_model']}'")

#         print("\n" + "="*50 + "\n")

# # Llamamos a la función para imprimir la información de todos los modelos
# print_model_info()
