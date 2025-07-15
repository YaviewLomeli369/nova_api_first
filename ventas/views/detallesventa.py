


from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import DetalleVenta
from ventas.serializers import DetalleVentaSerializer
from accounts.permissions import IsVendedor, IsEmpresaAdmin
from rest_framework.pagination import PageNumberPagination
import django_filters

# Clase de paginación personalizada
class DetalleVentaPagination(PageNumberPagination):
    page_size = 10  # Número de resultados por página
    page_size_query_param = 'page_size'
    max_page_size = 100  # Máximo número de resultados por página

# Filtro personalizado para Detalles de Venta
class DetalleVentaFilter(django_filters.FilterSet):
    # Filtro por fecha de la venta
    fecha_inicio = django_filters.DateFilter(field_name='venta__fecha', lookup_expr='gte', label='Fecha desde')
    fecha_fin = django_filters.DateFilter(field_name='venta__fecha', lookup_expr='lte', label='Fecha hasta')

    class Meta:
        model = DetalleVenta
        fields = ['venta', 'producto', 'fecha_inicio', 'fecha_fin']

class DetalleVentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Detalles de Venta
    """
    queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = DetalleVentaFilter  # Filtro personalizado
    pagination_class = DetalleVentaPagination  # Paginación personalizada

    # Permitimos ordenar por cantidad y precio_unitario
    ordering_fields = ['cantidad', 'precio_unitario']
    ordering = ['-cantidad']  # Orden predeterminado por cantidad descendente

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            return self.queryset
        # Filtrar detalles solo de ventas pertenecientes a la empresa del usuario
        return self.queryset.filter(venta__empresa=user.empresa)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)









# from rest_framework import viewsets, permissions
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import DetalleVenta
# from ventas.serializers import DetalleVentaSerializer
# from accounts.permissions import IsVendedor, IsEmpresaAdmin

# class DetalleVentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Detalles de Venta
#     """
#     queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
#     serializer_class = DetalleVentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['venta', 'producto']

#     def get_queryset(self):
#         user = self.request.user
#         if user.rol.nombre == "Superadministrador":
#             return self.queryset
#         # Filtrar detalles solo de ventas pertenecientes a la empresa del usuario
#         return self.queryset.filter(venta__empresa=user.empresa)






# from rest_framework import viewsets, permissions
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import DetalleVenta
# from ventas.serializers import DetalleVentaSerializer
# from accounts.permissions import IsVendedor, IsEmpresaAdmin

# class DetalleVentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Detalles de Venta
#     """
#     queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
#     serializer_class = DetalleVentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['venta', 'producto']