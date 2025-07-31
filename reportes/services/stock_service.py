from django.db.models import Sum, Q
from inventario.models import Inventario

def obtener_stock_actual_por_producto(
    empresa,
    sucursal=None,
    categoria_id=None,
    minimo_stock=False
):
    """
    Obtiene el stock actual agrupado por producto y categoría, filtrando por empresa,
    opcionalmente por sucursal y categoría.

    Parámetros:
    - empresa: instancia Empresa (obligatorio)
    - sucursal: instancia Sucursal o None (opcional)
    - categoria_id: int o None (opcional) para filtrar solo esa categoría
    - minimo_stock: bool, si True, solo productos con stock > 0

    Retorna: queryset de dicts con:
    - producto__id
    - producto__nombre
    - producto__codigo
    - producto__categoria__id
    - producto__categoria__nombre
    - stock_actual (Decimal)
    """

    filtros = Q(producto__empresa=empresa)
    if sucursal:
        filtros &= Q(sucursal=sucursal)
    if categoria_id:
        filtros &= Q(producto__categoria_id=categoria_id)

    queryset = (
        # Filtrar Inventarios según criterios
        # Se suman cantidades (stock actual)
        Inventario.objects
        .filter(filtros)
        .values(
            'producto__id',
            'producto__codigo',
            'producto__nombre',
            'producto__categoria__id',
            'producto__categoria__nombre',
        )
        .annotate(stock_actual=Sum('cantidad'))
        .order_by('producto__categoria__nombre', 'producto__nombre')
    )

    if minimo_stock:
        queryset = queryset.filter(stock_actual__gt=0)

    return queryset
