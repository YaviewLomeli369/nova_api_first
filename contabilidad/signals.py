from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetalleAsiento

@receiver([post_save, post_delete], sender=DetalleAsiento)
def actualizar_totales_asiento(sender, instance, **kwargs):
    instance.asiento.actualizar_totales()
    
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import DetalleAsiento

# def actualizar_totales(self):
#     detalles = self.detalles.all()
#     self.total_debe = sum(det.debe for det in detalles)
#     self.total_haber = sum(det.haber for det in detalles)
#     self.save(update_fields=['total_debe', 'total_haber'])

# @receiver([post_save, post_delete], sender=DetalleAsiento)
# def actualizar_totales_asiento(sender, instance, **kwargs):
#     instance.asiento.actualizar_totales()

