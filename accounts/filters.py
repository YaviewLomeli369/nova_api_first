# accounts/filters.py
import django_filters
from accounts.models import Auditoria

class AuditoriaFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    fecha_fin = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = Auditoria
        fields = {
            'usuario__username': ['exact', 'icontains'],
            'accion': ['exact', 'icontains'],
            'tabla_afectada': ['exact', 'icontains'],
        }
