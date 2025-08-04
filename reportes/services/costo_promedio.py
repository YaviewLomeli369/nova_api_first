# reportes/services/costo_promedio.py

from compras.models import DetalleCompra
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

def calcular_cppp(producto_id, empresa_id, fecha_inicio=None, fecha_fin=None, proveedor_id=None):
    compras = DetalleCompra.objects.filter(
        producto_id=producto_id,
        compra__empresa_id=empresa_id,
        compra__estado__in=["recibida", "pagada"],
        # compra__estado__in=["recibida", "pagada", "pendiente"]  # solo para pruebas

    )

    if fecha_inicio:
        compras = compras.filter(compra__fecha__gte=fecha_inicio)
    if fecha_fin:
        compras = compras.filter(compra__fecha__lte=fecha_fin)
    if proveedor_id:
        compras = compras.filter(compra__proveedor_id=proveedor_id)

    # Calcular total de unidades
    total_unidades = compras.aggregate(total=Sum('cantidad'))['total'] or Decimal("0")

    # Calcular total costo: cantidad * precio_unitario como Decimal
    total_costo_expr = ExpressionWrapper(
        F('cantidad') * F('precio_unitario'),
        output_field=DecimalField(max_digits=18, decimal_places=2)
    )
    total_costo = compras.aggregate(suma=Sum(total_costo_expr))['suma'] or Decimal("0.00")

    # Evitar división por cero
    if total_unidades > 0:
        cppp = (total_costo / total_unidades).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        cppp = Decimal("0.00")

    return {
        'producto_id': producto_id,
        'cppp': cppp,
        'total_compras': compras.count(),
        'total_unidades': total_unidades
    }
