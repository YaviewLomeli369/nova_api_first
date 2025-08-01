# compras/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from compras.models import PagoCompra, Compra
from django.db.models import Sum

@receiver(post_save, sender=PagoCompra)
def actualizar_fecha_pagada(sender, instance, **kwargs):
    compra = instance.compra
    total_pagado = compra.pagos.aggregate(total=Sum('monto'))['total'] or 0

    if total_pagado >= compra.total and not compra.fecha_pagada:
        compra.fecha_pagada = instance.fecha_pago  # Asegúrate que sea el campo correcto
        compra.save(update_fields=['fecha_pagada'])
