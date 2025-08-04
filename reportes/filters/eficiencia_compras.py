from django_filters import rest_framework as filters
from compras.models import Compra

class EficienciaComprasFilter(filters.FilterSet):
    fecha_inicio = filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_fin = filters.DateFilter(field_name='fecha', lookup_expr='lte')
    proveedor = filters.NumberFilter(field_name='proveedor__id')

    # Opcional: filtrar por categoría de producto en detalles de compra
    # categoria = filters.NumberFilter(field_name='detalles__producto__categoria', lookup_expr='exact')

    class Meta:
        model = Compra
        fields = ['empresa', 'fecha_inicio', 'fecha_fin', 'proveedor']  # Añade 'categoria' si lo activas arriba


