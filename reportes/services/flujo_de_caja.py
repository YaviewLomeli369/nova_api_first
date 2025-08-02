from collections import defaultdict
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Q
from finanzas.models import CuentaPorCobrar, CuentaPorPagar

def flujo_caja_proyectado(
    empresa,
    sucursal_id=None,
    fecha_inicio=None,
    fecha_fin=None,
    agrupacion='diaria',  # 'diaria' o 'mensual'
):
    if fecha_inicio is None:
        fecha_inicio = date.today()
    if fecha_fin is None:
        fecha_fin = fecha_inicio + timedelta(days=30)

    # --- Entradas ---
    filtros_cxc = Q(empresa=empresa, estado='PENDIENTE', fecha_vencimiento__range=(fecha_inicio, fecha_fin))
    if sucursal_id:
        filtros_cxc &= Q(venta__sucursal__id=sucursal_id)

    entradas = (
        CuentaPorCobrar.objects
        .filter(filtros_cxc)
        .values('fecha_vencimiento')
        .annotate(total=Sum('monto'))
    )

    # --- Salidas ---
    filtros_cxp = Q(empresa=empresa, estado='PENDIENTE', fecha_vencimiento__range=(fecha_inicio, fecha_fin))
    if sucursal_id:
        filtros_cxp &= Q(venta__sucursal__id=sucursal_id)

    salidas = (
        CuentaPorPagar.objects
        .filter(filtros_cxp)
        .values('fecha_vencimiento')
        .annotate(total=Sum('monto'))
    )

    flujo = defaultdict(lambda: {'entradas': Decimal('0.00'), 'salidas': Decimal('0.00')})

    for item in entradas:
        fecha = item['fecha_vencimiento']
        flujo[fecha]['entradas'] += item['total'] or Decimal('0.00')

    for item in salidas:
        fecha = item['fecha_vencimiento']
        flujo[fecha]['salidas'] += item['total'] or Decimal('0.00')

    # --- Agrupación ---
    if agrupacion == 'mensual':
        flujo_mensual = defaultdict(lambda: {'entradas': Decimal('0.00'), 'salidas': Decimal('0.00')})
        for fecha, valores in flujo.items():
            mes = fecha.strftime('%Y-%m')
            flujo_mensual[mes]['entradas'] += valores['entradas']
            flujo_mensual[mes]['salidas'] += valores['salidas']

        resultado = [
            {
                'periodo': mes,
                'entradas': datos['entradas'],
                'salidas': datos['salidas'],
                'saldo_neto': datos['entradas'] - datos['salidas'],
            }
            for mes, datos in sorted(flujo_mensual.items())
        ]
    else:
        resultado = [
            {
                'fecha': fecha,
                'entradas': datos['entradas'],
                'salidas': datos['salidas'],
                'saldo_neto': datos['entradas'] - datos['salidas'],
            }
            for fecha, datos in sorted(flujo.items())
        ]

    return resultado