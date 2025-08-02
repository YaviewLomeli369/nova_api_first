# reportes/services.py

from collections import defaultdict
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from ventas.models import Venta, DetalleVenta
from compras.models import DetalleCompra
from core.models import Empresa, Sucursal
from django.utils.dateparse import parse_date

def calcular_margen_bruto(empresa_id, sucursal_id=None, fecha_inicio=None, fecha_fin=None, agrupacion='mensual'):
    """
    Calcula el margen bruto para una empresa, opcionalmente por sucursal y rango de fechas,
    agrupado por día o mes.
    """
    # Validar fechas
    if fecha_inicio:
        fecha_inicio = parse_date(fecha_inicio)
    if fecha_fin:
        fecha_fin = parse_date(fecha_fin)

    # Filtrar ventas
    ventas_qs = Venta.objects.filter(empresa_id=empresa_id)
    if sucursal_id:
        ventas_qs = ventas_qs.filter(sucursal_id=sucursal_id)
    if fecha_inicio:
        ventas_qs = ventas_qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        ventas_qs = ventas_qs.filter(fecha__lte=fecha_fin)

    # Traer detalles con info necesaria
    detalles_qs = DetalleVenta.objects.filter(venta__in=ventas_qs).select_related('producto')

    # Agrupar por periodo (diario o mensual)
    resultado = defaultdict(lambda: {'ventas': 0, 'costo': 0, 'margen_bruto': 0})

    for detalle in detalles_qs:
        fecha_venta = detalle.venta.fecha
        periodo = fecha_venta.strftime('%Y-%m-%d') if agrupacion == 'diaria' else fecha_venta.strftime('%Y-%m')
        ingreso = detalle.cantidad * detalle.precio_unitario
        costo = detalle.cantidad * detalle.producto.precio_compra
        margen = ingreso - costo

        resultado[periodo]['ventas'] += float(ingreso)
        resultado[periodo]['costo'] += float(costo)
        resultado[periodo]['margen_bruto'] += float(margen)

    # Ordenar por periodo y convertir a lista
    lista_resultados = []
    for periodo in sorted(resultado.keys()):
        data = resultado[periodo]
        lista_resultados.append({
            'periodo': periodo,
            'ventas': round(data['ventas'], 2),
            'costo': round(data['costo'], 2),
            'margen_bruto': round(data['margen_bruto'], 2),
        })

    # Totales
    totales = {
        'ventas_total': sum(x['ventas'] for x in lista_resultados),
        'costo_total': sum(x['costo'] for x in lista_resultados),
        'margen_bruto_total': sum(x['margen_bruto'] for x in lista_resultados),
    }

    return {
        'detalle': lista_resultados,
        'totales': totales
    }
