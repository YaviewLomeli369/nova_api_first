from compras.models import Compra  # o como se llame tu modelo de compras
from django.db.models import Sum, F
from django.db.models import Sum, F, Count

def reporte_compras_por_proveedor(fecha_inicio=None, fecha_fin=None, proveedor_id=None):
    queryset = Compra.objects.all()

    if fecha_inicio:
        queryset = queryset.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__lte=fecha_fin)
    if proveedor_id:
        queryset = queryset.filter(proveedor_id=proveedor_id)

    resultado = (
        queryset
        .values('proveedor__id', 'proveedor__nombre')
        .annotate(
            total_compras=Sum('total'),  # Ajusta 'total' al campo correcto
            num_compras=Count('id')
        )
        .order_by('-total_compras')
    )

    return resultado
