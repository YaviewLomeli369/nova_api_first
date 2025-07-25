from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetalleAsiento

@receiver([post_save, post_delete], sender=DetalleAsiento)
def actualizar_totales_asiento(sender, instance, **kwargs):
    print(f"Signal disparado para DetalleAsiento id={instance.id}")
    asiento = instance.asiento
    if not asiento:
        print("¡El detalle no tiene asignado asiento!")
        return
    try:
        asiento.actualizar_totales()
        print(f"Asiento {asiento.id} actualizado: debe={asiento.total_debe}, haber={asiento.total_haber}")
    except Exception as e:
        print(f"Error actualizando totales del asiento {asiento.id}: {e}")