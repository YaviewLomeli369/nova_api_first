# core/filters.py

import django_filters
from core.models import Empresa, Sucursal


class EmpresaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    rfc = django_filters.CharFilter(field_name='rfc', lookup_expr='icontains')
    regimen_fiscal = django_filters.CharFilter(field_name='regimen_fiscal', lookup_expr='icontains')
    creado_en__gte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='gte')
    creado_en__lte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='lte')

    class Meta:
        model = Empresa
        fields = ['nombre', 'rfc', 'regimen_fiscal', 'creado_en__gte', 'creado_en__lte']


class SucursalFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    empresa = django_filters.NumberFilter(field_name='empresa__id')
    creado_en__gte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='gte')
    creado_en__lte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='lte')

    class Meta:
        model = Sucursal
        fields = ['nombre', 'empresa', 'creado_en__gte', 'creado_en__lte']



# # core/filters.py
# from django_filters import rest_framework as filters
# from core.models import Empresa

# class EmpresaFilter(filters.FilterSet):
#     rfc = filters.CharFilter(field_name='rfc', lookup_expr='icontains')
#     nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains')

#     class Meta:
#         model = Empresa
#         fields = ['rfc', 'nombre']
