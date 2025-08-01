from django.apps import AppConfig
# from compras.signals import post_save_compra,

class ComprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compras'

    def ready(self):
        import compras.signals