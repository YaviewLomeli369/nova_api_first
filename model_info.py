from django.apps import apps


def print_model_info():
    for model in apps.get_models():
        model_name = model._meta.model_name
        fields_info = []

        # Recorremos los campos y mostramos solo lo más esencial
        for field in model._meta.fields:
            if field.is_relation:
                related_model = field.related_model._meta.model_name
                fields_info.append(
                    f"{field.name} ({field.get_internal_type()}) -> {related_model}"
                )
            else:
                fields_info.append(
                    f"{field.name} ({field.get_internal_type()})")

        # Imprimir el modelo con sus campos
        print(f"{model_name}: {', '.join(fields_info)}")


# Ejecutar la función
print_model_info()

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
