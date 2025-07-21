# finanzas/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from finanzas.models import Pago
from contabilidad.models import AsientoContable

@receiver(post_delete, sender=Pago)
def eliminar_asiento_al_eliminar_pago(sender, instance, **kwargs):
    try:
        AsientoContable.objects.filter(
            referencia_id=instance.id,
            referencia_tipo='Pago',
            empresa=instance.empresa
        ).delete()
    except Exception as e:
        print(f"Error eliminando asiento contable al borrar pago: {e}")