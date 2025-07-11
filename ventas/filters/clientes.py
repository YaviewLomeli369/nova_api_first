# ventas/filters/clientes.py
import django_filters
from ventas.models import Cliente

class ClienteFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    rfc = django_filters.CharFilter(lookup_expr='icontains')
    correo = django_filters.CharFilter(lookup_expr='icontains')
    telefono = django_filters.CharFilter(lookup_expr='icontains')
    creado_en = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Cliente
        fields = ['empresa', 'nombre', 'rfc', 'correo', 'telefono', 'creado_en']
