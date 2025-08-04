# reportes/filters/costo_promedio.py
from django_filters import rest_framework as filters
from compras.models import DetalleCompra

class CostoPromedioFilter(filters.FilterSet):
    producto = filters.NumberFilter(field_name="producto__id")
    proveedor = filters.NumberFilter(field_name="compra__proveedor__id")
    fecha_inicio = filters.DateFilter(field_name="compra__fecha", lookup_expr="gte")
    fecha_fin = filters.DateFilter(field_name="compra__fecha", lookup_expr="lte")

    class Meta:
        model = DetalleCompra
        fields = ['producto', 'proveedor', 'fecha_inicio', 'fecha_fin']
