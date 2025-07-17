# compras/filters.py

import django_filters
from compras.models import Compra

class CompraFilter(django_filters.FilterSet):
    fecha_compra = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')

    class Meta:
        model = Compra
        fields = ['empresa', 'proveedor']
