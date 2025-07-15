import django_filters
from inventario.models import Producto
from django.db.models import Q
from django_filters import rest_framework as filters
from inventario.models import Inventario

class ProductoFilter(filters.FilterSet):
    nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains', label='Nombre contiene')
    descripcion = filters.CharFilter(field_name='descripcion', lookup_expr='icontains', label='Descripción contiene')
    precio_min = filters.NumberFilter(field_name='precio_venta', lookup_expr='gte', label='Precio mínimo')
    precio_max = filters.NumberFilter(field_name='precio_venta', lookup_expr='lte', label='Precio máximo')
    stock_min = filters.NumberFilter(field_name='stock', lookup_expr='gte', label='Stock mínimo')
    stock_max = filters.NumberFilter(field_name='stock', lookup_expr='lte', label='Stock máximo')
    fecha_vencimiento_desde = filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='gte')
    fecha_vencimiento_hasta = filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='lte')
    activo = filters.BooleanFilter(field_name='activo')
    categoria = filters.NumberFilter(field_name='categoria_id')
    proveedor = filters.NumberFilter(field_name='proveedor_id')

    class Meta:
        model = Producto
        fields = []



class InventarioFilter(django_filters.FilterSet):
    producto = django_filters.CharFilter(field_name='producto__nombre', lookup_expr='icontains', label="Nombre del producto")
    sucursal = django_filters.NumberFilter(field_name='sucursal__id', label="ID de sucursal")
    cantidad_min = django_filters.NumberFilter(field_name='cantidad', lookup_expr='gte', label="Cantidad mínima")
    cantidad_max = django_filters.NumberFilter(field_name='cantidad', lookup_expr='lte', label="Cantidad máxima")

    class Meta:
        model = Inventario
        fields = ['producto', 'sucursal', 'cantidad_min', 'cantidad_max']