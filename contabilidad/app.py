# def ready(self):
#   import contabilidad.signals  # cambia por el nombre real

from django.apps import AppConfig

class ContabilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contabilidad'

    def ready(self):
        import contabilidad.signals