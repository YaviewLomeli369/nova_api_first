# core/filters.py
from django_filters import rest_framework as filters
from core.models import Empresa

class EmpresaFilter(filters.FilterSet):
    rfc = filters.CharFilter(field_name='rfc', lookup_expr='icontains')
    nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains')

    class Meta:
        model = Empresa
        fields = ['rfc', 'nombre']
