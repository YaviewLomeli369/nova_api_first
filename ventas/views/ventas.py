from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Venta
from ventas.serializers import VentaSerializer
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor
import django_filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# Filtros personalizados para las ventas
class VentaFilter(django_filters.FilterSet):
    # Filtro para el RFC del cliente
    rfc_cliente = django_filters.CharFilter(field_name='cliente__rfc', lookup_expr='icontains', label='RFC del Cliente')

    # Filtro para el nombre del producto (en los detalles de la venta)
    nombre_producto = django_filters.CharFilter(field_name='detalles__producto__nombre', lookup_expr='icontains', label='Nombre del Producto')

    # Filtros de fecha (rango de fechas)
    fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte', label='Fecha desde')
    fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte', label='Fecha hasta')

    # Filtro para el vendedor
    vendedor = django_filters.CharFilter(field_name='usuario__username', lookup_expr='icontains', label='Vendedor')

    # Filtro para el estado de la venta
    estado = django_filters.ChoiceFilter(choices=Venta.ESTADO_CHOICES, label='Estado')

    class Meta:
        model = Venta
        fields = ['empresa', 'estado', 'cliente', 'fecha_inicio', 'fecha_fin', 'rfc_cliente', 'nombre_producto', 'vendedor']


# Clase de paginación personalizada
class VentaPagination(PageNumberPagination):
    page_size = 10  # Número de resultados por página
    page_size_query_param = 'page_size'
    max_page_size = 100  # Máximo número de resultados por página


class VentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Ventas, con detalles anidados.
    """
    queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles__producto')
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['cliente__nombre', 'usuario__username', 'estado']
    filterset_class = VentaFilter  # Usamos el filtro personalizado aquí

    # Configuramos la paginación
    pagination_class = VentaPagination

    # Ordenamiento por fecha o total
    ordering_fields = ['fecha', 'total']  # Permite ordenar por fecha y total
    ordering = ['-fecha']  # Orden por defecto: por fecha descendente

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            return self.queryset
        return self.queryset.filter(empresa=user.empresa)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def get_latest_sales(self):
        """
        Devuelve las últimas n ventas con filtros aplicados.
        """
        n = self.request.query_params.get('n', 10)  # Número de ventas a devolver
        try:
            n = int(n)
        except ValueError:
            n = 10  # Si no se pasa un número válido, devolver las últimas 10 ventas

        # Filtrar las ventas según los parámetros de búsqueda
        filtered_sales = self.filter_queryset(self.queryset.order_by('-fecha')[:n])

        # Devuelve las ventas filtradas y limitadas
        return filtered_sales

    def list(self, request, *args, **kwargs):
        """
        Sobrescribimos el método `list` para agregar soporte para obtener las últimas 'n' ventas.
        """
        # Si se pasa el parámetro 'latest', devolver solo las últimas 'n' ventas
        if 'latest' in self.request.query_params:
            latest_sales = self.get_latest_sales()
            page = self.paginate_queryset(latest_sales)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(self.get_serializer(latest_sales, many=True).data)

        # Si no se pide 'latest', proceder con la lógica predeterminada
        return super().list(request, *args, **kwargs)





# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import Venta, DetalleVenta
# from ventas.serializers import VentaSerializer
# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor
# import django_filters

# # Filtros personalizados para las ventas
# class VentaFilter(django_filters.FilterSet):
#     # Filtro para el RFC del cliente
#     rfc_cliente = django_filters.CharFilter(field_name='cliente__rfc', lookup_expr='icontains', label='RFC del Cliente')

#     # Filtro para el nombre del producto (en los detalles de la venta)
#     nombre_producto = django_filters.CharFilter(field_name='detalles__producto__nombre', lookup_expr='icontains', label='Nombre del Producto')

#     # Filtros de fecha (rango de fechas)
#     fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte', label='Fecha desde')
#     fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte', label='Fecha hasta')

#     # Filtro para el vendedor
#     vendedor = django_filters.CharFilter(field_name='usuario__username', lookup_expr='icontains', label='Vendedor')

#     # Filtro para el estado de la venta
#     estado = django_filters.ChoiceFilter(choices=Venta.ESTADO_CHOICES, label='Estado')

#     class Meta:
#         model = Venta
#         fields = ['empresa', 'estado', 'cliente', 'fecha_inicio', 'fecha_fin', 'rfc_cliente', 'nombre_producto', 'vendedor']


# class VentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Ventas, con detalles anidados.
#     """
#     queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles__producto')
#     serializer_class = VentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['cliente__nombre', 'usuario__username', 'estado']
#     filterset_class = VentaFilter  # Usamos el filtro personalizado aquí

#     def get_queryset(self):
#         user = self.request.user
#         if user.rol.nombre == "Superadministrador":
#             return self.queryset
#         return self.queryset.filter(empresa=user.empresa)

#     def perform_create(self, serializer):
#         serializer.save(usuario=self.request.user)






# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import Venta
# from ventas.serializers import VentaSerializer
# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor

# class VentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Ventas, con detalles anidados.
#     """
#     queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles')
#     serializer_class = VentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['cliente__nombre', 'usuario__username', 'estado']
#     filterset_fields = ['empresa', 'estado', 'fecha', 'cliente']

#     def get_queryset(self):
#         user = self.request.user
#         if user.rol.nombre == "Superadministrador":
#             return self.queryset
#         return self.queryset.filter(empresa=user.empresa)

#     def perform_create(self, serializer):
#         serializer.save(usuario=self.request.user)


