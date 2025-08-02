from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Q, Sum
from django.utils.dateparse import parse_date
from finanzas.models import CuentaPorCobrar, CuentaPorPagar


def flujo_caja_proyectado(sucursal_id=None, fecha_inicio=None, fecha_fin=None, agrupacion='mensual'):
    """
    Genera un reporte de flujo de caja proyectado basado en las cuentas por cobrar y pagar.

    Args:
        sucursal_id: ID de la sucursal (opcional)
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha de fin del período  
        agrupacion: 'diaria' o 'mensual'

    Returns:
        dict: Datos del flujo de caja proyectado
    """

    # Filtros base
    filtros_cxc = Q()
    filtros_cxp = Q()

    if fecha_inicio:
        filtros_cxc &= Q(fecha_vencimiento__gte=fecha_inicio)
        filtros_cxp &= Q(fecha_vencimiento__gte=fecha_inicio)

    if fecha_fin:
        filtros_cxc &= Q(fecha_vencimiento__lte=fecha_fin)
        filtros_cxp &= Q(fecha_vencimiento__lte=fecha_fin)

    if sucursal_id:
        # CuentaPorCobrar tiene relación: venta -> sucursal
        filtros_cxc &= Q(venta__sucursal_id=sucursal_id)
        # CuentaPorPagar NO tiene relación directa con sucursal
        # Filtraremos por empresa (asumiendo que sucursal pertenece a una empresa)
        from core.models import Sucursal
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_cxp &= Q(empresa_id=sucursal.empresa_id)
        except Sucursal.DoesNotExist:
            # Si no existe la sucursal, no aplicar filtro adicional
            pass

    # Consultas
    cuentas_cobrar = CuentaPorCobrar.objects.filter(filtros_cxc)
    cuentas_pagar = CuentaPorPagar.objects.filter(filtros_cxp)

    # Agrupar por período
    flujo_data = defaultdict(lambda: {'entradas': 0, 'salidas': 0})

    for cuenta in cuentas_cobrar:
        periodo = _obtener_periodo(cuenta.fecha_vencimiento, agrupacion)
        flujo_data[periodo]['entradas'] += float(cuenta.saldo_pendiente)

    for cuenta in cuentas_pagar:
        periodo = _obtener_periodo(cuenta.fecha_vencimiento, agrupacion)
        flujo_data[periodo]['salidas'] += float(cuenta.saldo_pendiente)

    # Convertir a lista ordenada
    flujo_caja = []
    for periodo in sorted(flujo_data.keys()):
        data = flujo_data[periodo]
        flujo_caja.append({
            'periodo': periodo,
            'entradas': round(data['entradas'], 2),
            'salidas': round(data['salidas'], 2),
            'saldo_neto': round(data['entradas'] - data['salidas'], 2)
        })

    return {
        'flujo_caja': flujo_caja,
        'total_entradas': sum(item['entradas'] for item in flujo_caja),
        'total_salidas': sum(item['salidas'] for item in flujo_caja),
        'saldo_neto_total': sum(item['saldo_neto'] for item in flujo_caja)
    }


def _obtener_periodo(fecha, agrupacion):
    """Obtiene el período de agrupación para una fecha dada."""
    if agrupacion == 'diaria':
        return fecha.strftime('%Y-%m-%d')
    else:  # mensual
        return fecha.strftime('%Y-%m')