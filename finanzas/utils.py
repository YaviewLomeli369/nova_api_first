# finanzas/utils.py
from django.utils.timezone import now
from datetime import timedelta
from finanzas.models import CuentaPorCobrar

def cuentas_por_vencer():
    hoy = now().date()
    limite = hoy + timedelta(days=3)
    return CuentaPorCobrar.objects.filter(fecha_vencimiento__range=(hoy, limite), estado='PENDIENTE')
