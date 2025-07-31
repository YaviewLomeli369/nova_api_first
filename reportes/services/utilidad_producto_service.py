# reportes/services/utilidad_producto_service.py

from ventas.models import DetalleVenta
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from datetime import datetime
from django.utils.timezone import make_aware

def reporte_utilidad_por_producto(fecha_inicio, fecha_fin, empresa, sucursal=None):
    # Convertir fechas si vienen como string
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.fromisoformat(fecha_inicio).date()
    if isinstance(fecha_fin, str):
        fecha_fin = datetime.fromisoformat(fecha_fin).date()
    
    # Si las fechas son objetos date, convertir a datetime para el rango
    if hasattr(fecha_inicio, 'date') and callable(fecha_inicio.date):
        fecha_inicio = fecha_inicio.date()
    if hasattr(fecha_fin, 'date') and callable(fecha_fin.date):
        fecha_fin = fecha_fin.date()

    # Base queryset: filtrar por empresa y fechas
    qs = DetalleVenta.objects.filter(
        venta__fecha__date__range=(fecha_inicio, fecha_fin),
        venta__empresa=empresa,
        venta__estado='COMPLETADA',  # Muy importante
    )

    # Filtro opcional por sucursal
    if sucursal:
        qs = qs.filter(venta__sucursal=sucursal)

    # Anotar cálculos
    qs = qs.values(
        'producto_id',
        'producto__nombre'
    ).annotate(
        cantidad_vendida=Sum('cantidad'),
        ingresos_ventas=Sum(
            ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=FloatField())
        ),
        costo_total=Sum(
            ExpressionWrapper(F('cantidad') * F('producto__precio_compra'), output_field=FloatField())
        )
    ).annotate(
        utilidad_bruta=ExpressionWrapper(
            F('ingresos_ventas') - F('costo_total'),
            output_field=FloatField()
        )
    ).order_by('-utilidad_bruta')

    return qs