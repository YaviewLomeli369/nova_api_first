# ventas/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from .models import DetalleVenta, Venta

def actualizar_total_venta(venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
    except Venta.DoesNotExist:
        return  # Si no existe, nada que hacer

    total = venta.detalles.aggregate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    )['total'] or 0

    # Actualizar solo si cambió para evitar saves innecesarios
    if venta.total != total:
        venta.total = total
        venta.save(update_fields=['total'])

@receiver(post_save, sender=DetalleVenta)
def detalleventa_guardado(sender, instance, **kwargs):
    actualizar_total_venta(instance.venta_id)

@receiver(post_delete, sender=DetalleVenta)
def detalleventa_eliminado(sender, instance, **kwargs):
    actualizar_total_venta(instance.venta_id)
