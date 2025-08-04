import django_filters
from ventas.models import Venta
from core.models import Empresa, Sucursal
from datetime import datetime, date, time, timedelta


class RotacionInventarioFilter(django_filters.FilterSet):
    empresa = django_filters.ModelChoiceFilter(field_name='empresa', queryset=Empresa.objects.all(), required=True)
    sucursal = django_filters.ModelChoiceFilter(field_name='sucursal', queryset=Sucursal.objects.all(), required=False)
    fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte', required=True)
    fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte', required=True)

    class Meta:
        model = Venta
        fields = ['empresa', 'sucursal', 'fecha_inicio', 'fecha_fin']