from ventas.models import Venta
from django.db.models import Sum, Count
from datetime import datetime

def calcular_promedio_ticket(empresa_id, fecha_inicio=None, fecha_fin=None):
    ventas = Venta.objects.filter(
        empresa_id=empresa_id,
        estado='COMPLETADA'
    )

    if fecha_inicio:
        ventas = ventas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__lte=fecha_fin)

    total_tickets = ventas.count()
    total_ingresos = ventas.aggregate(suma_total=Sum('total'))['suma_total'] or 0

    promedio_ticket = total_ingresos / total_tickets if total_tickets > 0 else 0

    return {
        'total_tickets': total_tickets,
        'total_ingresos': total_ingresos,
        'promedio_ticket': promedio_ticket
    }
