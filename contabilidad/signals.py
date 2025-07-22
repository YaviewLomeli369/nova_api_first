from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetalleAsiento

@receiver([post_save, post_delete], sender=DetalleAsiento)
def actualizar_totales_asiento(sender, instance, **kwargs):
    instance.asiento.actualizar_totales()
    

