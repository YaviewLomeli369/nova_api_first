from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from ventas.models import DetalleVenta
from inventario.models import Categoria

def categorias_mas_rentables(
    empresa,
    sucursal_id=None,
    fecha_inicio=None,
    fecha_fin=None,
    pagina=1,
    items_por_pagina=10,
):
    filtros = Q(venta__empresa=empresa) & Q(venta__estado='COMPLETADA')

    if sucursal_id:
        filtros &= Q(venta__sucursal_id=sucursal_id)
    if fecha_inicio:
        filtros &= Q(venta__fecha__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(venta__fecha__lte=fecha_fin)

    queryset = (
        DetalleVenta.objects.filter(filtros)
        .values(
            'producto__categoria__id',
            'producto__categoria__nombre',
        )
        .annotate(
            total_ingresos=Sum(F('precio_unitario') * F('cantidad'), output_field=DecimalField(max_digits=20, decimal_places=2)),
            total_costos=Sum(F('producto__precio_compra') * F('cantidad'), output_field=DecimalField(max_digits=20, decimal_places=2)),
        )
        .annotate(
            utilidad=ExpressionWrapper(F('total_ingresos') - F('total_costos'), output_field=DecimalField(max_digits=20, decimal_places=2))
        )
        .order_by('-utilidad')
    )

    # Paginación manual simple
    start = (pagina - 1) * items_por_pagina
    end = start + items_por_pagina
    total = queryset.count()
    resultados = list(queryset[start:end])

    return {
        'total': total,
        'pagina': pagina,
        'items_por_pagina': items_por_pagina,
        'resultados': resultados,
    }
