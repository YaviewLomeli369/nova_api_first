# reportes/services/kpi.py
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from ventas.models import DetalleVenta
from datetime import datetime



def obtener_rentabilidad_por_producto_y_cliente(empresa_id, fecha_inicio=None, fecha_fin=None, cliente_id=None, producto_id=None):
    """
    Obtiene rentabilidad agrupada por producto y cliente, filtrando por empresa y opcionalmente por fechas, cliente y producto.
    """
    detalles = DetalleVenta.objects.filter(
        venta__empresa_id=empresa_id,
        venta__estado='COMPLETADA',
    )

    if fecha_inicio:
        detalles = detalles.filter(venta__fecha__gte=fecha_inicio)
    if fecha_fin:
        detalles = detalles.filter(venta__fecha__lte=fecha_fin)
    if cliente_id:
        detalles = detalles.filter(venta__cliente_id=cliente_id)
    if producto_id:
        detalles = detalles.filter(producto_id=producto_id)

    detalles = detalles.annotate(
        importe=F('cantidad') * F('precio_unitario'),
        costo_total=F('cantidad') * F('producto__precio_compra'),
        utilidad=ExpressionWrapper(
            (F('cantidad') * F('precio_unitario')) - (F('cantidad') * F('producto__precio_compra')),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    resultado = detalles.values(
        'producto_id',
        'producto__nombre',
        'venta__cliente_id',
        'venta__cliente__nombre',
    ).annotate(
        total_venta=Sum('importe'),
        costo_venta=Sum('costo_total'),
        utilidad_total=Sum('utilidad'),
    ).order_by('producto__nombre', 'venta__cliente__nombre')

    return resultado
