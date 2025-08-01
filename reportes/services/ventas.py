from ventas.models import Venta
from django.db.models import Sum, Count
from datetime import datetime
from ventas.models import DetalleVenta
from django.db.models import Sum
from inventario.models import Producto

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
def obtener_productos_mas_vendidos(empresa, limite=10, fecha_inicio=None, fecha_fin=None):
    """
    Retorna los productos más vendidos por cantidad (TOP N), opcionalmente filtrando por fechas.
    """
    filtros = {'venta__empresa': empresa}
    if fecha_inicio:
        filtros['venta__fecha__gte'] = fecha_inicio
    if fecha_fin:
        filtros['venta__fecha__lte'] = fecha_fin

    queryset = (
        DetalleVenta.objects
        .filter(**filtros)
        .values('producto__id', 'producto__nombre', 'producto__codigo')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:limite]
    )

    return list(queryset)