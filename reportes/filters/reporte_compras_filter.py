import django_filters
from compras.models import Compra

class ReporteComprasFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')
    proveedor = django_filters.NumberFilter(field_name='proveedor__id')

    class Meta:
        model = Compra
        fields = ['fecha_inicio', 'fecha_fin', 'proveedor']
