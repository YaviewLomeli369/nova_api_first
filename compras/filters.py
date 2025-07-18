# compras/filters.py

import django_filters
from compras.models import Compra

class CompraFilter(django_filters.FilterSet):
    # Rango de fechas
    fecha_min = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_max = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')

    # Rango de totales
    total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')

    # Filtro exacto por nombre de producto
    nombre_producto = django_filters.CharFilter(method='filter_nombre_producto')

    # Filtros por ID o múltiples productos
    producto_id = django_filters.NumberFilter(field_name='detalles__producto__id')
    producto_id__in = django_filters.BaseInFilter(field_name='detalles__producto__id', lookup_expr='in')

    class Meta:
        model = Compra
        fields = ['empresa', 'proveedor', 'estado']

    def filter_nombre_producto(self, queryset, name, value):
        return queryset.filter(detalles__producto__nombre__icontains=value).distinct()