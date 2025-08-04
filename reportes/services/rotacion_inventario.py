# reportes/services/rotacion_inventario.py

from decimal import Decimal
from django.db.models import Sum, F, Q
from ventas.models import DetalleVenta
from inventario.models import Producto, Inventario
from core.models import Empresa
from datetime import datetime


def calcular_rotacion_inventario(empresa_id, fecha_inicio, fecha_fin):
    """
    Calcula la rotación de inventario para una empresa entre dos fechas.
    """
    empresa = Empresa.objects.get(id=empresa_id)

    # 1. Obtener productos de la empresa
    productos = Producto.objects.filter(empresa=empresa)

    # 2. Calcular stock al inicio del período
    inventarios_inicio = Inventario.objects.filter(producto__in=productos)
    stock_inicio = inventarios_inicio.aggregate(
        total=Sum('cantidad')
    )['total'] or Decimal('0')

    # 3. Calcular stock al final del período (usamos el mismo, asumido actual)
    inventarios_fin = inventarios_inicio  # Igual por ahora
    stock_fin = inventarios_fin.aggregate(
        total=Sum('cantidad')
    )['total'] or Decimal('0')

    # 4. Calcular stock promedio
    stock_promedio = (stock_inicio + stock_fin) / 2 if (stock_inicio + stock_fin) > 0 else Decimal('0')

    # 5. Costo de ventas real = sum(cantidad vendida * precio_compra del producto)
    detalles = DetalleVenta.objects.filter(
        venta__empresa=empresa,
        venta__estado='COMPLETADA',
        venta__fecha__range=[fecha_inicio, fecha_fin]
    ).annotate(
        costo=F('cantidad') * F('producto__precio_compra')
    )

    costo_ventas = detalles.aggregate(
        total=Sum('costo')
    )['total'] or Decimal('0')

    # 6. Calcular rotación
    rotacion = costo_ventas / stock_promedio if stock_promedio > 0 else Decimal('0')

    return {
        "periodo": f"{fecha_inicio} a {fecha_fin}",
        "costo_ventas": round(costo_ventas, 2),
        "stock_promedio": round(stock_promedio, 2),
        "rotacion": round(rotacion, 2)
    }

# # reportes/services/rotacion_inventario.py

# from collections import defaultdict
# from django.utils.dateparse import parse_date
# from ventas.models import DetalleVenta
# from inventario.models import MovimientoInventario
# from datetime import timedelta

# def calcular_rotacion_inventario(empresa_id, sucursal_id=None, fecha_inicio=None, fecha_fin=None, agrupacion='mensual'):
#     if fecha_inicio:
#         fecha_inicio = parse_date(str(fecha_inicio))
#     if fecha_fin:
#         fecha_fin = parse_date(str(fecha_fin))

#     # Filtrar ventas para costo ventas
#     ventas_qs = DetalleVenta.objects.filter(producto__empresa_id=empresa_id)
#     if sucursal_id:
#         ventas_qs = ventas_qs.filter(venta__sucursal_id=sucursal_id)
#     if fecha_inicio:
#         ventas_qs = ventas_qs.filter(venta__fecha__gte=fecha_inicio)
#     if fecha_fin:
#         ventas_qs = ventas_qs.filter(venta__fecha__lte=fecha_fin)

#     costos_por_periodo = defaultdict(float)
#     for dv in ventas_qs.select_related('producto', 'venta'):
#         fecha = dv.venta.fecha
#         periodo = fecha.strftime('%Y-%m') if agrupacion == 'mensual' else fecha.strftime('%Y-%m-%d')
#         costo = float(dv.cantidad) * float(dv.producto.precio_compra)
#         costos_por_periodo[periodo] += costo

#     # Filtrar movimientos para inventario
#     movimientos_qs = MovimientoInventario.objects.filter(inventario__producto__empresa_id=empresa_id)
#     if sucursal_id:
#         movimientos_qs = movimientos_qs.filter(inventario__sucursal_id=sucursal_id)
#     if fecha_inicio:
#         movimientos_qs = movimientos_qs.filter(fecha__gte=fecha_inicio - timedelta(days=30))
#     if fecha_fin:
#         movimientos_qs = movimientos_qs.filter(fecha__lte=fecha_fin)

#     movimientos_por_periodo = defaultdict(float)
#     for m in movimientos_qs.select_related('inventario', 'inventario__producto'):
#         fecha = m.fecha
#         periodo = fecha.strftime('%Y-%m') if agrupacion == 'mensual' else fecha.strftime('%Y-%m-%d')
#         cantidad = float(m.cantidad)
#         # Ajusta según tus tipos de movimiento, aquí asumo 'entrada' y 'salida'
#         if m.tipo_movimiento.lower() in ['entrada', 'compra', 'ajuste_entrada']:
#             movimientos_por_periodo[periodo] += cantidad
#         else:
#             movimientos_por_periodo[periodo] -= cantidad

#     resultados = []
#     periodos = sorted(costos_por_periodo.keys())
#     for i, periodo in enumerate(periodos):
#         costo_ventas = costos_por_periodo.get(periodo, 0)
#         inventario_inicial = movimientos_por_periodo.get(periodos[i-1], 0) if i > 0 else 0
#         inventario_final = movimientos_por_periodo.get(periodo, 0)
#         inventario_promedio = (inventario_inicial + inventario_final) / 2 if (inventario_inicial or inventario_final) else 0
#         rotacion = (costo_ventas / inventario_promedio) if inventario_promedio else 0
#         dias_periodo = 30 if agrupacion == 'mensual' else 1
#         dias_promedio_inventario = (dias_periodo / rotacion) if rotacion else None

#         resultados.append({
#             "periodo": periodo,
#             "costo_ventas": round(costo_ventas, 2),
#             "inventario_inicial": round(inventario_inicial, 2),
#             "inventario_final": round(inventario_final, 2),
#             "inventario_promedio": round(inventario_promedio, 2),
#             "rotacion": round(rotacion, 2),
#             "dias_promedio_inventario": round(dias_promedio_inventario, 2) if dias_promedio_inventario else None,
#         })

#     costo_total = sum(x["costo_ventas"] for x in resultados)
#     inventario_promedio_total = (sum(x["inventario_promedio"] for x in resultados) / len(resultados)) if resultados else 0
#     rotacion_promedio = (costo_total / inventario_promedio_total) if inventario_promedio_total else 0
#     dias_promedio_total = (30 / rotacion_promedio) if rotacion_promedio else None

#     return {
#         "count": len(resultados),
#         "results": resultados,
#         "totales": {
#             "costo_total": round(costo_total, 2),
#             "inventario_promedio_total": round(inventario_promedio_total, 2),
#             "rotacion_promedio": round(rotacion_promedio, 2),
#             "dias_promedio_total": round(dias_promedio_total, 2) if dias_promedio_total else None,
#         },
#         "agrupacion": agrupacion,
#         "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
#         "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
#     }
